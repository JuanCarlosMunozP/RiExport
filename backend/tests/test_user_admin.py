import asyncio
import json
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from pydantic import SecretStr

from core.config import settings
from core.errors import APIError, install_exception_handlers
from core.security import create_access_token
from database.session import get_db
from users.router import router as users_router


@pytest.fixture
def auth_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        SecretStr("test-user-admin-secret".ljust(64, "!")),
    )
    monkeypatch.setattr(settings, "jwt_issuer", "riexport-user-admin-test")


def _test_app(session: Mock) -> FastAPI:
    app = FastAPI()
    app.include_router(users_router, prefix="/api/v1")

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    install_exception_handlers(app)
    return app


def _patch(
    app: FastAPI,
    path: str,
    *,
    token: str,
    payload: dict[str, object] | None = None,
) -> tuple[int, dict[str, object]]:
    messages: list[dict[str, object]] = []
    body = json.dumps(payload or {}).encode()
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "PATCH",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": [
            (b"content-type", b"application/json"),
            (b"authorization", f"Bearer {token}".encode()),
        ],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }
    received = False

    async def receive() -> dict[str, object]:
        nonlocal received
        if received:
            return {"type": "http.disconnect"}
        received = True
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    asyncio.run(app(scope, receive, send))
    start = next(m for m in messages if m["type"] == "http.response.start")
    response_body = b"".join(
        m.get("body", b"") for m in messages if m["type"] == "http.response.body"
    )
    return int(start["status"]), json.loads(response_body)


def _user(user_id: int, *, is_active: bool = True) -> SimpleNamespace:
    now = datetime.now(UTC)
    return SimpleNamespace(
        id=user_id,
        email="ana@example.com",
        first_name="Ana",
        last_name="Pérez",
        phone=None,
        role_id=3,
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


def test_updates_only_requested_fields(auth_settings: None) -> None:
    actor = _user(4)
    target = _user(9)
    session = Mock()
    session.get.side_effect = [actor, target]
    session.scalar.return_value = "users.update"

    status, payload = _patch(
        _test_app(session),
        "/api/v1/users/9",
        token=create_access_token(4),
        payload={"first_name": "  Ana María  "},
    )

    assert status == 200
    assert payload["first_name"] == "Ana María"
    assert payload["last_name"] == "Pérez"
    assert payload["email"] == "ana@example.com"
    assert target.first_name == "Ana María"
    assert target.last_name == "Pérez"
    session.commit.assert_called_once()


def test_deactivation_rejects_the_authenticated_user(auth_settings: None) -> None:
    session = Mock()
    session.get.return_value = _user(4)
    session.scalar.return_value = "users.deactivate"

    status, payload = _patch(
        _test_app(session),
        "/api/v1/users/4/deactivate",
        token=create_access_token(4),
    )

    assert status == 409
    assert payload["error"]["code"] == "CONFLICT"
    session.commit.assert_not_called()


def test_deactivation_requires_permission(auth_settings: None) -> None:
    session = Mock()
    session.get.return_value = _user(4)
    session.scalar.return_value = None

    status, _payload = _patch(
        _test_app(session),
        "/api/v1/users/9/deactivate",
        token=create_access_token(4),
    )

    assert status == 403
    session.commit.assert_not_called()


def test_last_active_administrator_cannot_be_deactivated() -> None:
    from users.service import deactivate_user

    administrator = _user(9)
    administrator.role_id = 2
    session = Mock()
    session.get.side_effect = [administrator, SimpleNamespace(name="administrador")]
    session.scalar.return_value = 1

    with pytest.raises(APIError) as error:
        deactivate_user(session, 9, actor_id=4)

    assert error.value.status_code == 409
    session.commit.assert_not_called()
