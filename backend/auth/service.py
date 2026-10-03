"""Authentication use cases."""

from sqlalchemy.orm import Session

from auth.schemas import LoginRequest, TokenResponse
from core.config import settings
from core.errors import APIError
from core.security import create_access_token, verify_password
from users import repository

_DUMMY_PASSWORD_HASH = "$2b$12$M1jKNzET1c1AKV.7m1ss4eJosce0hon.V0RUQgREHs2tBNip3sdCu"


def login(session: Session, request: LoginRequest) -> TokenResponse:
    email = str(request.email)
    user = repository.get_user_by_email(session, email)
    if user is None:
        verify_password(request.password, _DUMMY_PASSWORD_HASH)
        raise _invalid_credentials()
    if not verify_password(request.password, user.password_hash):
        raise _invalid_credentials()
    if not user.is_active or not user.role.is_active:
        raise _invalid_credentials()

    return TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


def _invalid_credentials() -> APIError:
    return APIError(
        status_code=401,
        code="UNAUTHORIZED",
        message="Correo electrónico o contraseña incorrectos.",
        headers={"WWW-Authenticate": "Bearer"},
    )
