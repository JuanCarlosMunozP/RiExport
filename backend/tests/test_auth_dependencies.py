from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import SecretStr

from auth.dependencies import get_current_user
from core.config import settings
from core.errors import APIError
from core.security import create_access_token
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
