import asyncio
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import SecretStr

from auth.dependencies import CurrentUser, get_current_user
from core.config import settings
from core.errors import APIError, install_exception_handlers
from core.security import create_access_token
from database.session import get_db
from users.models import AppUser


@pytest.fixture
def auth_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        SecretStr("test-auth-dependency-secret".ljust(64, "!")),
    )
    monkeypatch.setattr(settings, "jwt_issuer", "riexport-auth-test")


def test_authenticated_dependency_returns_active_database_user(
    auth_settings: None,
) -> None:
    user = SimpleNamespace(is_active=True)
    session = Mock()
    session.get.return_value = user
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=create_access_token(42)
    )

    resolved = get_current_user(credentials, session)

    assert resolved is user
    session.get.assert_called_once_with(AppUser, 42)


@pytest.mark.parametrize(
    "credentials",
    [
        None,
        HTTPAuthorizationCredentials(scheme="Basic", credentials="not-a-bearer-token"),
        HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid"),
    ],
)
def test_missing_or_invalid_token_returns_uniform_401(
    auth_settings: None,
    credentials: HTTPAuthorizationCredentials | None,
) -> None:
    with pytest.raises(APIError) as error:
        get_current_user(credentials, Mock())

    assert error.value.status_code == 401
    assert error.value.code == "UNAUTHORIZED"
    assert error.value.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize("user", [None, SimpleNamespace(is_active=False)])
def test_unknown_or_inactive_user_is_rejected(
    auth_settings: None,
    user: SimpleNamespace | None,
) -> None:
    session = Mock()
    session.get.return_value = user
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=create_access_token(42)
    )

    with pytest.raises(APIError) as error:
        get_current_user(credentials, session)

    assert error.value.status_code == 401
    assert error.value.message == "Se requiere autenticación válida."


def test_non_numeric_subject_is_rejected(auth_settings: None) -> None:
    session = Mock()
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=create_access_token("not-a-user-id")
    )

    with pytest.raises(APIError) as error:
        get_current_user(credentials, session)

    assert error.value.status_code == 401
    session.get.assert_not_called()


def test_fastapi_route_can_inject_authenticated_user(
    auth_settings: None,
) -> None:
    user = SimpleNamespace(id=42, is_active=True)
    session = Mock()
    session.get.return_value = user
    app = FastAPI()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    install_exception_handlers(app)

    @app.get("/protected")
    def protected(current_user: CurrentUser) -> dict[str, int]:
        return {"user_id": current_user.id}

    status, _headers, body = _asgi_get(
        app,
        "/protected",
        [(b"authorization", f"Bearer {create_access_token(42)}".encode())],
    )

    assert status == 200
    assert body == b'{"user_id":42}'
    session.get.assert_called_once_with(AppUser, 42)


def test_fastapi_protected_route_rejects_missing_token() -> None:
    app = FastAPI()
    install_exception_handlers(app)

    @app.get("/protected")
    def protected(user: CurrentUser) -> dict[str, int]:
        return {"user_id": user.id}

    status, headers, body = _asgi_get(app, "/protected")

    assert status == 401
    assert dict(headers)[b"www-authenticate"] == b"Bearer"
    assert b'"code":"UNAUTHORIZED"' in body


def _asgi_get(
    app: FastAPI,
    path: str,
    headers: list[tuple[bytes, bytes]] | None = None,
) -> tuple[int, list[tuple[bytes, bytes]], bytes]:
    messages: list[dict[str, object]] = []
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": headers or [],
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
    return start["status"], start["headers"], body
