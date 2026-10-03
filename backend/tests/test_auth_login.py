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
from auth.router import router as auth_router
from core.config import settings
from core.errors import install_exception_handlers
from core.security import decode_access_token, hash_password
from database.session import get_db


@pytest.fixture
def auth_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        SecretStr("test-auth-login-secret".ljust(64, "!")),
    )
    monkeypatch.setattr(settings, "jwt_issuer", "riexport-auth-login-test")
    monkeypatch.setattr(settings, "jwt_access_token_expire_minutes", 30)


@pytest.fixture
def active_user() -> SimpleNamespace:
    now = datetime.now(UTC)
    return SimpleNamespace(
        id=42,
        email="ana@example.com",
        password_hash=hash_password("correct password"),
        is_active=True,
        role=SimpleNamespace(is_active=True),
        created_at=now,
        updated_at=now,
    )


def _app(session: Mock) -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router, prefix="/api/v1")

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    install_exception_handlers(app)
    return app


def _post(
    app: FastAPI,
    body: dict[str, object],
) -> tuple[int, list[tuple[bytes, bytes]], dict[str, object]]:
    messages: list[dict[str, object]] = []
    encoded_body = json.dumps(body).encode()
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/auth/login",
        "raw_path": b"/api/v1/auth/login",
        "query_string": b"",
        "root_path": "",
        "headers": [(b"content-type", b"application/json")],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }
    sent_body = False

    async def receive() -> dict[str, object]:
        nonlocal sent_body
        if sent_body:
            return {"type": "http.disconnect"}
        sent_body = True
        return {"type": "http.request", "body": encoded_body, "more_body": False}

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    asyncio.run(app(scope, receive, send))
    response_start = next(
        message for message in messages if message["type"] == "http.response.start"
    )
    response_body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return (
        int(response_start["status"]),
        response_start["headers"],
        json.loads(response_body),
    )


def test_login_normalizes_email_and_returns_bearer_token(
    auth_settings: None,
    active_user: SimpleNamespace,
) -> None:
    session = Mock()
    session.scalar.return_value = active_user

    status, _headers, body = _post(
        _app(session),
        {"email": " ANA@EXAMPLE.COM ", "password": "correct password"},
    )

    assert status == 200
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 1800
    claims = decode_access_token(body["access_token"])
    assert claims["sub"] == "42"
    assert "password" not in body
    query = session.scalar.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "ana@example.com" in query.params.values()


@pytest.mark.parametrize(
    ("user_state", "password"),
    [
        (None, "correct password"),
        ("active", "incorrect password"),
        ("inactive", "correct password"),
        ("inactive_role", "correct password"),
    ],
)
def test_login_rejects_invalid_or_inactive_accounts_uniformly(
    auth_settings: None,
    active_user: SimpleNamespace,
    user_state: str | None,
    password: str,
) -> None:
    if user_state == "inactive":
        active_user.is_active = False
    elif user_state == "inactive_role":
        active_user.role.is_active = False

    session = Mock()
    session.scalar.return_value = None if user_state is None else active_user

    status, headers, body = _post(
        _app(session),
        {"email": "ana@example.com", "password": password},
    )

    assert status == 401
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert body["error"]["message"] == "Correo electrónico o contraseña incorrectos."
    assert dict(headers)[b"www-authenticate"] == b"Bearer"


def test_login_rejects_extra_fields_before_database_lookup(
    auth_settings: None,
) -> None:
    session = Mock()

    status, _headers, body = _post(
        _app(session),
        {
            "email": "ana@example.com",
            "password": "correct password",
            "role_id": 1,
        },
    )

    assert status == 422
    assert body["error"]["code"] == "VALIDATION_ERROR"
    session.scalar.assert_not_called()
