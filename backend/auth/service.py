"""Authentication use cases."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import update
from sqlalchemy.orm import Session

from auth.schemas import (
    LoginRequest,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    TokenResponse,
)
from core.config import settings
from core.errors import APIError
from core.security import create_access_token, verify_password
from users import repository
from users.models import PasswordResetToken

_DUMMY_PASSWORD_HASH = "$2b$12$M1jKNzET1c1AKV.7m1ss4eJosce0hon.V0RUQgREHs2tBNip3sdCu"
_PASSWORD_RESET_TTL = timedelta(minutes=30)
_PASSWORD_RESET_MESSAGE = (
    "Si existe una cuenta activa con ese correo, recibirá instrucciones "
    "para recuperar el acceso."
)


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


def request_password_reset(
    session: Session, request: PasswordResetRequest
) -> PasswordResetRequestResponse:
    user = repository.get_user_by_email(session, str(request.email))
    if user is not None and user.is_active and user.role.is_active:
        now = datetime.now(UTC)
        token = secrets.token_urlsafe(32)
        session.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=now)
        )
        session.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
                expires_at=now + _PASSWORD_RESET_TTL,
            )
        )
        session.commit()

    return PasswordResetRequestResponse(message=_PASSWORD_RESET_MESSAGE)


def _invalid_credentials() -> APIError:
    return APIError(
        status_code=401,
        code="UNAUTHORIZED",
        message="Correo electrónico o contraseña incorrectos.",
        headers={"WWW-Authenticate": "Bearer"},
    )
