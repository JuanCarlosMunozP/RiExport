from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
import pytest
from pydantic import SecretStr

from core.config import settings
from core.security import (
    BCRYPT_MAX_PASSWORD_BYTES,
    BCRYPT_ROUNDS,
    JWT_ALGORITHM,
    InvalidAccessToken,
    TokenConfigurationError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_uses_bcrypt_and_random_salt() -> None:
    password = "Cafe-y-cacao-2026!"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash.startswith(f"$2b${BCRYPT_ROUNDS:02d}$")
    assert first_hash != second_hash
    assert len(first_hash) == 60
    assert password not in first_hash
    assert bcrypt.checkpw(password.encode("utf-8"), first_hash.encode("ascii"))


def test_verify_password_accepts_only_the_matching_password() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert verify_password("correct horse battery staple", password_hash)
    assert not verify_password("incorrect password", password_hash)


def test_hash_rejects_passwords_over_bcrypt_byte_limit() -> None:
    assert len("ñ".encode() * (BCRYPT_MAX_PASSWORD_BYTES // 2)) == 72
    hash_password("ñ" * (BCRYPT_MAX_PASSWORD_BYTES // 2))

    with pytest.raises(ValueError, match="72 bytes"):
        hash_password("ñ" * (BCRYPT_MAX_PASSWORD_BYTES // 2 + 1))


@pytest.mark.parametrize(
    ("password", "stored_hash"),
    [
        ("secret", "not-a-bcrypt-hash"),
        ("secret", ""),
        ("x" * (BCRYPT_MAX_PASSWORD_BYTES + 1), "not-a-bcrypt-hash"),
    ],
)
def test_verify_returns_false_for_invalid_hash_or_oversized_password(
    password: str, stored_hash: str
) -> None:
    assert not verify_password(password, stored_hash)


def test_password_with_null_byte_is_rejected_and_fails_verification() -> None:
    with pytest.raises(ValueError, match="nulos"):
        hash_password("pass\x00word")

    assert not verify_password("pass\x00word", "not-a-bcrypt-hash")


@pytest.fixture
def jwt_settings(monkeypatch: pytest.MonkeyPatch) -> bytes:
    key = b"test-only-jwt-signing-key".ljust(64, b"!")
    monkeypatch.setattr(settings, "jwt_secret_key", SecretStr(key.decode()))
    monkeypatch.setattr(settings, "jwt_issuer", "riexport-test")
    monkeypatch.setattr(settings, "jwt_access_token_expire_minutes", 30)
    return key


def test_access_token_round_trip_has_required_claims_only(jwt_settings: bytes) -> None:
    token = create_access_token(42)
    claims = decode_access_token(token)

    assert claims["sub"] == "42"
    assert claims["iss"] == "riexport-test"
    assert claims["token_use"] == "access"
    assert claims["exp"] - claims["iat"] == 30 * 60
    assert claims["jti"]
    assert "role" not in claims
    assert "permissions" not in claims
    assert jwt.get_unverified_header(token)["alg"] == JWT_ALGORITHM


def test_token_supports_a_positive_custom_lifetime(jwt_settings: bytes) -> None:
    token = create_access_token("user-1", expires_delta=timedelta(minutes=5))

    assert (
        decode_access_token(token)["exp"] - decode_access_token(token)["iat"] == 5 * 60
    )


@pytest.mark.parametrize("token", ["", "not-a-jwt", "a.b.c"])
def test_decode_rejects_malformed_access_tokens(
    jwt_settings: bytes, token: str
) -> None:
    with pytest.raises(InvalidAccessToken):
        decode_access_token(token)


def test_decode_rejects_wrong_signature_and_expired_token(jwt_settings: bytes) -> None:
    invalid_signature = jwt.encode(
        {"sub": "42", "iss": "riexport-test"},
        b"different-signing-key-for-invalid-signature".ljust(64, b"!"),
        algorithm=JWT_ALGORITHM,
    )
    now = datetime.now(UTC)
    unsupported_algorithm = jwt.encode(
        {
            "sub": "42",
            "iss": "riexport-test",
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "jti": "wrong-algorithm",
            "token_use": "access",
        },
        jwt_settings,
        algorithm="HS384",
    )
    expired = jwt.encode(
        {
            "sub": "42",
            "iss": "riexport-test",
            "iat": now - timedelta(minutes=2),
            "exp": now - timedelta(minutes=1),
            "jti": "expired-token",
            "token_use": "access",
        },
        jwt_settings,
        algorithm=JWT_ALGORITHM,
    )

    for token in (invalid_signature, unsupported_algorithm, expired):
        with pytest.raises(InvalidAccessToken):
            decode_access_token(token)


def test_token_issuer_and_use_must_match(jwt_settings: bytes) -> None:
    now = datetime.now(UTC)
    claims = {
        "sub": "42",
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "jti": "wrong-token-kind",
        "iss": "riexport-test",
        "token_use": "password_reset",
    }
    token = jwt.encode(claims, jwt_settings, algorithm=JWT_ALGORITHM)

    with pytest.raises(InvalidAccessToken):
        decode_access_token(token)


@pytest.mark.parametrize("secret", [None, SecretStr("too-short")])
def test_issuing_token_requires_a_strong_configured_secret(
    monkeypatch: pytest.MonkeyPatch, secret: SecretStr | None
) -> None:
    monkeypatch.setattr(settings, "jwt_secret_key", secret)

    with pytest.raises(TokenConfigurationError):
        create_access_token("42")
