import bcrypt
import pytest

from core.security import (
    BCRYPT_MAX_PASSWORD_BYTES,
    BCRYPT_ROUNDS,
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
