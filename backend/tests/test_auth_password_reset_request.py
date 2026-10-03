import hashlib
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from auth.schemas import PasswordResetRequest
from auth.service import request_password_reset
from users.models import PasswordResetToken


def test_request_reset_stores_only_hash_and_uses_generic_response() -> None:
    user = SimpleNamespace(
        id=17,
        is_active=True,
        role=SimpleNamespace(is_active=True),
    )
    session = Mock()
    session.scalar.return_value = user

    response = request_password_reset(
        session,
        PasswordResetRequest(email="ANA@example.com"),
    )

    token = session.add.call_args.args[0]
    assert isinstance(token, PasswordResetToken)
    assert token.user_id == user.id
    assert len(token.token_hash) == 64
    assert token.expires_at > datetime.now(UTC) + timedelta(minutes=29)
    assert response.message == (
        "Si existe una cuenta activa con ese correo, recibirá instrucciones "
        "para recuperar el acceso."
    )
    assert token.token_hash != hashlib.sha256(response.message.encode()).hexdigest()
    session.execute.assert_called_once()
    session.commit.assert_called_once()


@pytest.mark.parametrize(
    "account",
    [
        None,
        SimpleNamespace(id=17, is_active=False, role=SimpleNamespace(is_active=True)),
        SimpleNamespace(id=17, is_active=True, role=SimpleNamespace(is_active=False)),
    ],
)
def test_request_reset_does_not_create_tokens_for_unknown_or_inactive_accounts(
    account: SimpleNamespace | None,
) -> None:
    session = Mock()
    session.scalar.return_value = account

    response = request_password_reset(
        session,
        PasswordResetRequest(email="ana@example.com"),
    )

    assert "Si existe una cuenta activa" in response.message
    session.add.assert_not_called()
    session.execute.assert_not_called()
    session.commit.assert_not_called()


def test_request_reset_normalizes_email_and_rejects_extra_fields() -> None:
    request = PasswordResetRequest(email=" ANA@EXAMPLE.COM ")
    assert str(request.email) == "ana@example.com"

    with pytest.raises(ValueError):
        PasswordResetRequest(email="ana@example.com", user_id=17)
