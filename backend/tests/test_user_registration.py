import asyncio
import json
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from pydantic import SecretStr
from sqlalchemy.dialects import postgresql

import database.models  # noqa: F401
from core.config import settings
from core.errors import install_exception_handlers
from core.security import create_access_token, verify_password
from database.session import get_db
from users.models import AppUser
from users.router import router as users_router


@pytest.fixture
def auth_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        SecretStr("test-user-registration-secret".ljust(64, "!")),
    )
    monkeypatch.setattr(settings, "jwt_issuer", "riexport-user-registration-test")


def _test_app(session: Mock) -> FastAPI:
    app = FastAPI()
    app.include_router(users_router, prefix="/api/v1")

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    install_exception_handlers(app)
    return app


def _post_json(
    app: FastAPI,
    path: str,
    payload: dict[str, object],
    *,
    token: str | None = None,
) -> tuple[int, list[tuple[bytes, bytes]], bytes]:
    messages: list[dict[str, object]] = []
    body = json.dumps(payload).encode()
    headers = [(b"content-type", b"application/json")]
    if token is not None:
        headers.append((b"authorization", f"Bearer {token}".encode()))
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": headers,
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }
    has_received_body = False

    async def receive() -> dict[str, object]:
        nonlocal has_received_body
        if has_received_body:
            return {"type": "http.disconnect"}
        has_received_body = True
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    asyncio.run(app(scope, receive, send))
    start = next(
        message for message in messages if message["type"] == "http.response.start"
    )
    response_body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return start["status"], start["headers"], response_body


def _valid_payload(**updates: object) -> dict[str, object]:
    return {
        "email": " New.User@Example.com ",
        "password": "correct horse battery staple",
        "first_name": " Ana ",
        "last_name": " García ",
        "phone": " +57 300 123 4567 ",
        "role_id": 8,
        **updates,
    }


def _session_for_authorized_actor() -> tuple[Mock, SimpleNamespace]:
    actor = SimpleNamespace(id=4, role_id=2, is_active=True)
    role = SimpleNamespace(id=8, is_active=True)
    session = Mock()
    session.get.side_effect = [actor, role]
    session.scalar.side_effect = ["users.create", None]

    def refresh(user: AppUser) -> None:
        now = datetime.now(UTC)
        user.id = 77
        user.is_active = True
        user.created_at = now
        user.updated_at = now

    session.add.side_effect = lambda user: None
    session.refresh.side_effect = refresh
    return session, actor


def test_registers_user_with_normalized_fields_and_hashed_password(
    auth_settings: None,
) -> None:
    session, _ = _session_for_authorized_actor()
    response_status, _headers, response_body = _post_json(
        _test_app(session),
        "/api/v1/users",
        _valid_payload(),
        token=create_access_token(4),
    )
    payload = json.loads(response_body)
    created_user = session.add.call_args.args[0]

    assert response_status == 201
    assert {
        key: value
        for key, value in payload.items()
        if key
        not in {
            "created_at",
            "updated_at",
        }
    } == {
        "id": 77,
        "email": "new.user@example.com",
        "first_name": "Ana",
        "last_name": "García",
        "phone": "+57 300 123 4567",
        "role_id": 8,
        "is_active": True,
    }
    assert datetime.fromisoformat(payload["created_at"]) == created_user.created_at
    assert datetime.fromisoformat(payload["updated_at"]) == created_user.updated_at
    assert verify_password("correct horse battery staple", created_user.password_hash)
    assert "password" not in payload
    assert "password_hash" not in payload
    permission_query = str(
        session.scalar.call_args_list[0].args[0].compile(dialect=postgresql.dialect())
    )
    assert "role_permission" in permission_query
    assert "is_active IS true" in permission_query
    session.commit.assert_called_once()


def test_registration_requires_authentication() -> None:
    session = Mock()
    status_code, headers, body = _post_json(
        _test_app(session), "/api/v1/users", _valid_payload()
    )

    assert status_code == 401
    assert dict(headers)[b"www-authenticate"] == b"Bearer"
    assert b'"code":"UNAUTHORIZED"' in body
    session.get.assert_not_called()


def test_registration_requires_users_create_permission(
    auth_settings: None,
) -> None:
    session = Mock()
    session.get.return_value = SimpleNamespace(id=4, role_id=2, is_active=True)
    session.scalar.return_value = None
    status_code, _headers, body = _post_json(
        _test_app(session),
        "/api/v1/users",
        _valid_payload(),
        token=create_access_token(4),
    )

    assert status_code == 403
    assert b'"code":"FORBIDDEN"' in body
    session.add.assert_not_called()


def test_duplicate_email_returns_conflict(auth_settings: None) -> None:
    actor = SimpleNamespace(id=4, role_id=2, is_active=True)
    session = Mock()
    session.get.return_value = actor
    session.scalar.side_effect = ["users.create", 51]
    status_code, _headers, body = _post_json(
        _test_app(session),
        "/api/v1/users",
        _valid_payload(),
        token=create_access_token(4),
    )

    assert status_code == 409
    assert b'"code":"CONFLICT"' in body
    session.add.assert_not_called()


@pytest.mark.parametrize("role", [None, SimpleNamespace(id=8, is_active=False)])
def test_missing_or_inactive_role_returns_validation_error(
    auth_settings: None,
    role: SimpleNamespace | None,
) -> None:
    actor = SimpleNamespace(id=4, role_id=2, is_active=True)
    session = Mock()
    session.get.side_effect = [actor, role]
    session.scalar.side_effect = ["users.create", None]
    status_code, _headers, body = _post_json(
        _test_app(session),
        "/api/v1/users",
        _valid_payload(),
        token=create_access_token(4),
    )

    assert status_code == 422
    assert b'"field":"role_id"' in body
    session.add.assert_not_called()


@pytest.mark.parametrize(
    ("updates", "field"),
    [
        ({"email": "not-an-email"}, b'"field":"email"'),
        ({"unexpected": "value"}, b'"field":"unexpected"'),
        ({"password": "ñ" * 37}, b'"field":"password"'),
    ],
)
def test_invalid_request_is_rejected(
    auth_settings: None,
    updates: dict[str, object],
    field: bytes,
) -> None:
    session, _ = _session_for_authorized_actor()
    status_code, _headers, body = _post_json(
        _test_app(session),
        "/api/v1/users",
        _valid_payload(**updates),
        token=create_access_token(4),
    )

    assert status_code == 422
    assert field in body
    session.add.assert_not_called()
