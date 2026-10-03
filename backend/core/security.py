"""Password hashing and verification helpers."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from core.config import settings

BCRYPT_ROUNDS = 12
BCRYPT_MAX_PASSWORD_BYTES = 72
JWT_ALGORITHM = "HS256"
JWT_MIN_SECRET_BYTES = 32


class TokenConfigurationError(RuntimeError):
    """Raised when JWT signing configuration is absent or unsafe."""


class InvalidAccessToken(ValueError):
    """Raised when an access token is invalid, expired, or otherwise unusable."""


def _jwt_signing_key() -> bytes:
    configured_secret = settings.jwt_secret_key
    if configured_secret is None:
        raise TokenConfigurationError("JWT_SECRET_KEY no está configurado.")

    key = configured_secret.get_secret_value().encode("utf-8")
    if len(key) < JWT_MIN_SECRET_BYTES:
        raise TokenConfigurationError(
            "JWT_SECRET_KEY debe contener al menos 32 bytes UTF-8."
        )
    return key


def create_access_token(
    subject: str | int,
    *,
    expires_delta: timedelta | None = None,
) -> str:
    """Issue a signed access token for a user identifier."""
    subject_value = str(subject)
    if not subject_value:
        raise ValueError("El sujeto del token es obligatorio.")

    now = datetime.now(UTC)
    token_lifetime = expires_delta or timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    if token_lifetime <= timedelta(0):
        raise ValueError("La duración del token debe ser positiva.")

    claims = {
        "sub": subject_value,
        "iat": now,
        "exp": now + token_lifetime,
        "iss": settings.jwt_issuer,
        "jti": uuid4().hex,
        "token_use": "access",
    }
    return jwt.encode(claims, _jwt_signing_key(), algorithm=JWT_ALGORITHM)


def decode_access_token(encoded_token: str) -> dict[str, Any]:
    """Validate an access token and return its claims."""
    try:
        claims = jwt.decode(
            encoded_token,
            _jwt_signing_key(),
            algorithms=[JWT_ALGORITHM],
            issuer=settings.jwt_issuer,
            options={
                "require": ["sub", "iat", "exp", "iss", "jti", "token_use"],
            },
        )
    except (InvalidTokenError, TypeError, UnicodeEncodeError, ValueError):
        raise InvalidAccessToken("El token de acceso no es válido.") from None

    if not isinstance(claims.get("sub"), str) or not claims["sub"]:
        raise InvalidAccessToken("El token de acceso no es válido.")
    if claims.get("token_use") != "access":
        raise InvalidAccessToken("El token de acceso no es válido.")
    return claims


def _encode_password(password: str) -> bytes:
    if not isinstance(password, str):
        raise TypeError("La contraseña debe ser texto.")

    password_bytes = password.encode("utf-8")
    if b"\x00" in password_bytes:
        raise ValueError("La contraseña no puede contener bytes nulos.")
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError("La contraseña supera el límite de 72 bytes UTF-8 de bcrypt.")
    return password_bytes


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with an automatically generated salt."""
    password_bytes = _encode_password(password)
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(password_bytes, salt).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    """Return whether a plaintext password matches a stored bcrypt hash."""
    try:
        password_bytes = _encode_password(password)
        hash_bytes = password_hash.encode("ascii")
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except (AttributeError, UnicodeEncodeError, TypeError, ValueError):
        return False
