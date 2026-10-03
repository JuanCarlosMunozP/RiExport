import asyncio
import json
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from urllib.parse import urlencode

import pytest
from fastapi import FastAPI
from pydantic import SecretStr
from sqlalchemy.dialects import postgresql

import database.models  # noqa: F401
from core.config import settings
from core.errors import install_exception_handlers
from core.security import create_access_token
from database.session import get_db
from roles.router import router as roles_router
from users.router import router as users_router


@pytest.fixture
def auth_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        SecretStr("test-user-query-secret".ljust(64, "!")),
    )
    monkeypatch.setattr(settings, "jwt_issuer", "riexport-user-query-test")


def _test_app(session: Mock) -> FastAPI:
    app = FastAPI()
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(roles_router, prefix="/api/v1")

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    install_exception_handlers(app)
    return app


def _get_json(
    app: FastAPI,
    query_parameters: dict[str, str],
    *,
    token: str | None = None,
    path: str = "/api/v1/users",
) -> tuple[int, bytes]:
    messages: list[dict[str, object]] = []
    query_string = urlencode(query_parameters).encode()
    headers = (
        [(b"authorization", f"Bearer {token}".encode())] if token is not None else []
    )
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": query_string,
        "root_path": "",
        "headers": headers,
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    asyncio.run(app(scope, receive, send))
    start = next(
        message for message in messages if message["type"] == "http.response.start"
    )
    body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return start["status"], body


@pytest.mark.parametrize(
    ("user_id", "path", "expected_status"),
    [
        (1, "/api/v1/users", 200),
        (1, "/api/v1/roles", 200),
        (2, "/api/v1/users", 200),
        (2, "/api/v1/roles", 403),
        (3, "/api/v1/users", 403),
        (3, "/api/v1/roles", 403),
    ],
)
def test_access_is_granted_by_role_permission_assignments(
    auth_settings: None,
    user_id: int,
    path: str,
    expected_status: int,
) -> None:
    grants = {
        1: {"users.read", "roles.read"},
        2: {"users.read"},
        3: set(),
    }
    users = {
        1: SimpleNamespace(id=1, role_id=1, is_active=True),
        2: SimpleNamespace(id=2, role_id=2, is_active=True),
        3: SimpleNamespace(id=3, role_id=3, is_active=True),
    }
    session = Mock()
    session.get.side_effect = lambda _model, identifier: users.get(identifier)
    session.scalar.side_effect = lambda statement: _resolve_permission(
        statement, grants
    )
    session.scalars.return_value.all.return_value = []

    status_code, body = _get_json(
        _test_app(session),
        {},
        token=create_access_token(user_id),
        path=path,
    )

    assert status_code == expected_status
    if expected_status == 403:
        assert b'"code":"FORBIDDEN"' in body


def _resolve_permission(statement, grants: dict[int, set[str]]) -> str | int | None:
    params = statement.compile().params
    permission_code = params.get("permission_code_1")
    if permission_code is not None:
        role_id = params["role_id_1"]
        return permission_code if permission_code in grants[role_id] else None
    return 0


def _user(user_id: int, email: str, *, is_active: bool = True):
    now = datetime.now(UTC)
    return SimpleNamespace(
        id=user_id,
        email=email,
        first_name="User",
        last_name=str(user_id),
        phone=None,
        role_id=3,
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


def test_queries_users_with_search_filters_and_pagination(
    auth_settings: None,
) -> None:
    session = Mock()
    session.get.return_value = SimpleNamespace(id=4, role_id=2, is_active=True)
    session.scalar.side_effect = ["users.read", 2]
    session.scalars.return_value.all.return_value = [
        _user(13, "ana@example.com"),
        _user(12, "ana2@example.com", is_active=False),
    ]

    status_code, body = _get_json(
        _test_app(session),
        {
            "q": "ana%_",
            "role_id": "3",
            "is_active": "false",
            "limit": "2",
            "offset": "4",
        },
        token=create_access_token(4),
    )
    payload = json.loads(body)

    assert status_code == 200
    assert [user["id"] for user in payload["items"]] == [13, 12]
    assert "password" not in payload["items"][0]
    assert "password_hash" not in payload["items"][0]
    assert payload["pagination"] == {"limit": 2, "offset": 4, "total": 2}

    count_query = str(
        session.scalar.call_args_list[1].args[0].compile(dialect=postgresql.dialect())
    )
    assert "ILIKE" in count_query
    assert "role_id = " in count_query
    assert "is_active IS false" in count_query
    assert (
        "%ana\\%\\_%"
        in session.scalar.call_args_list[1]
        .args[0]
        .compile(dialect=postgresql.dialect())
        .params.values()
    )

    list_query = str(
        session.scalars.call_args.args[0].compile(dialect=postgresql.dialect())
    )
    assert "LIMIT" in list_query
    assert "OFFSET" in list_query


def test_user_query_requires_users_read_permission(
    auth_settings: None,
) -> None:
    session = Mock()
    session.get.return_value = SimpleNamespace(id=4, role_id=2, is_active=True)
    session.scalar.return_value = None

    status_code, body = _get_json(_test_app(session), {}, token=create_access_token(4))

    assert status_code == 403
    assert b'"code":"FORBIDDEN"' in body
    session.scalars.assert_not_called()


def test_user_query_rejects_invalid_pagination(
    auth_settings: None,
) -> None:
    session = Mock()
    session.get.return_value = SimpleNamespace(id=4, role_id=2, is_active=True)
    session.scalar.return_value = "users.read"

    status_code, body = _get_json(
        _test_app(session), {"limit": "101"}, token=create_access_token(4)
    )

    assert status_code == 422
    assert b'"code":"VALIDATION_ERROR"' in body
    session.scalars.assert_not_called()
