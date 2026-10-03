"""Password hashing and verification helpers."""

import bcrypt

BCRYPT_ROUNDS = 12
BCRYPT_MAX_PASSWORD_BYTES = 72


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
