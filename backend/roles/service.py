"""Role and permission administration use cases."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.errors import APIError
from roles import repository
from roles.models import Role
from roles.schemas import (
    CreateRoleRequest,
    PermissionListResponse,
    PermissionResponse,
    RoleListResponse,
    RoleResponse,
    SetRolePermissionsRequest,
    UpdateRoleRequest,
)

_ADMIN_REQUIRED_PERMISSIONS = {
    "roles.read",
    "roles.create",
    "roles.update",
    "roles.permissions.update",
}


def list_roles(session: Session, *, include_inactive: bool) -> RoleListResponse:
    roles = repository.list_roles(session, include_inactive=include_inactive)
    return RoleListResponse(items=[_role_response(role) for role in roles])


def list_permissions(session: Session) -> PermissionListResponse:
    return PermissionListResponse(
        items=[
            PermissionResponse.model_validate(permission)
            for permission in repository.list_permissions(session)
        ]
    )


def create_role(session: Session, request: CreateRoleRequest) -> RoleResponse:
    if repository.get_role_by_name(session, request.name) is not None:
        raise _duplicate_role_error()
    role = Role(name=request.name, description=request.description)
    try:
        repository.add_role(session, role)
        session.commit()
        session.refresh(role)
    except IntegrityError:
        session.rollback()
        if repository.get_role_by_name(session, request.name) is not None:
            raise _duplicate_role_error() from None
        raise
    return _role_response(role)


def update_role(
    session: Session,
    role_id: int,
    request: UpdateRoleRequest,
) -> RoleResponse:
    role = _require_role(session, role_id)
    changes = request.model_dump(exclude_unset=True)
    if role.name == "administrador" and changes.get("name", role.name) != role.name:
        raise APIError(
            status_code=409,
            code="CONFLICT",
            message="No se puede cambiar el nombre del rol administrador del sistema.",
        )
    new_name = changes.get("name")
    if new_name is not None:
        existing = repository.get_role_by_name(session, new_name)
        if existing is not None and existing.id != role_id:
            raise _duplicate_role_error()
    for field, value in changes.items():
        setattr(role, field, value)
    try:
        session.commit()
        session.refresh(role)
    except IntegrityError:
        session.rollback()
        if new_name is not None and repository.get_role_by_name(session, new_name):
            raise _duplicate_role_error() from None
        raise
    return _role_response(role)


def set_role_permissions(
    session: Session,
    role_id: int,
    request: SetRolePermissionsRequest,
) -> RoleResponse:
    role = _require_role(session, role_id)
    codes = request.permission_codes
    if len(codes) != len(set(codes)):
        raise _invalid_permissions("No se permiten permisos duplicados.")
    available = repository.get_permissions_by_codes(session, codes)
    if {permission.code for permission in available} != set(codes):
        raise _invalid_permissions("Uno o más permisos no existen.")
    if role.name == "administrador" and not _ADMIN_REQUIRED_PERMISSIONS.issubset(
        set(codes)
    ):
        raise APIError(
            status_code=409,
            code="CONFLICT",
            message="El rol administrador debe conservar sus permisos de gestión.",
        )
    repository.replace_role_permissions(session, role_id, codes)
    session.commit()
    session.refresh(role)
    return _role_response(role, permission_codes=codes)


def deactivate_role(session: Session, role_id: int) -> RoleResponse:
    role = _require_role(session, role_id)
    if role.name == "administrador":
        raise APIError(
            status_code=409,
            code="CONFLICT",
            message="No se puede desactivar el rol administrador del sistema.",
        )
    if repository.active_user_count_for_role(session, role_id) > 0:
        raise APIError(
            status_code=409,
            code="CONFLICT",
            message="El rol tiene usuarios activos asignados.",
        )
    role.is_active = False
    session.commit()
    session.refresh(role)
    return _role_response(role)


def _require_role(session: Session, role_id: int) -> Role:
    role = repository.get_role(session, role_id)
    if role is None:
        raise APIError(
            status_code=404,
            code="NOT_FOUND",
            message="No se encontró el rol solicitado.",
        )
    return role


def _role_response(
    role: Role,
    *,
    permission_codes: list[str] | None = None,
) -> RoleResponse:
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        is_active=role.is_active,
        permission_codes=sorted(
            permission_codes
            if permission_codes is not None
            else [assignment.permission_code for assignment in role.permissions]
        ),
    )


def _duplicate_role_error() -> APIError:
    return APIError(
        status_code=409,
        code="CONFLICT",
        message="Ya existe un rol con ese nombre.",
    )


def _invalid_permissions(message: str) -> APIError:
    return APIError(
        status_code=422,
        code="VALIDATION_ERROR",
        message=message,
    )
