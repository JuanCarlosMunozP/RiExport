from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from core.errors import APIError
from roles.schemas import CreateRoleRequest, SetRolePermissionsRequest
from roles.service import deactivate_role, set_role_permissions


def test_role_name_is_normalized_for_storage() -> None:
    request = CreateRoleRequest(name=" Supervisor Logístico ")

    assert request.name == "supervisor_logístico"


def test_administrator_must_keep_role_management_permissions() -> None:
    administrator = SimpleNamespace(id=1, name="administrador")
    session = Mock()
    session.get.return_value = administrator

    with pytest.raises(APIError) as error:
        set_role_permissions(
            session,
            1,
            SetRolePermissionsRequest(permission_codes=[]),
        )

    assert error.value.status_code == 409
    session.execute.assert_not_called()
    session.commit.assert_not_called()


def test_unknown_permission_is_rejected() -> None:
    session = Mock()
    session.get.return_value = SimpleNamespace(id=2, name="usuario_comercial")
    session.scalars.return_value.all.return_value = []

    with pytest.raises(APIError) as error:
        set_role_permissions(
            session,
            2,
            SetRolePermissionsRequest(permission_codes=["users.unknown"]),
        )

    assert error.value.status_code == 422
    session.execute.assert_not_called()


def test_role_with_active_users_cannot_be_deactivated() -> None:
    session = Mock()
    session.get.return_value = SimpleNamespace(
        id=3,
        name="usuario_comercial",
        description=None,
        is_active=True,
        permissions=[],
    )
    session.scalar.return_value = 1

    with pytest.raises(APIError) as error:
        deactivate_role(session, 3)

    assert error.value.status_code == 409
    session.commit.assert_not_called()
