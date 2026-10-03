from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from auth.dependencies import require_permission
from database.session import get_db
from roles import service
from roles.schemas import (
    CreateRoleRequest,
    PermissionListResponse,
    RoleListResponse,
    RoleResponse,
    SetRolePermissionsRequest,
    UpdateRoleRequest,
)
from users.models import AppUser

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=RoleListResponse)
def query_roles(
    session: Annotated[Session, Depends(get_db)],
    _authorized_user: Annotated[AppUser, Depends(require_permission("roles.read"))],
    include_inactive: bool = False,
) -> RoleListResponse:
    return service.list_roles(session, include_inactive=include_inactive)


@router.get("/permissions", response_model=PermissionListResponse)
def query_permissions(
    session: Annotated[Session, Depends(get_db)],
    _authorized_user: Annotated[AppUser, Depends(require_permission("roles.read"))],
) -> PermissionListResponse:
    return service.list_permissions(session)


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    request: CreateRoleRequest,
    session: Annotated[Session, Depends(get_db)],
    _authorized_user: Annotated[AppUser, Depends(require_permission("roles.create"))],
) -> RoleResponse:
    return service.create_role(session, request)


@router.patch("/{role_id}", response_model=RoleResponse)
def edit_role(
    role_id: Annotated[int, Path(ge=1, le=2**63 - 1)],
    request: UpdateRoleRequest,
    session: Annotated[Session, Depends(get_db)],
    _authorized_user: Annotated[AppUser, Depends(require_permission("roles.update"))],
) -> RoleResponse:
    return service.update_role(session, role_id, request)


@router.put("/{role_id}/permissions", response_model=RoleResponse)
def assign_permissions(
    role_id: Annotated[int, Path(ge=1, le=2**63 - 1)],
    request: SetRolePermissionsRequest,
    session: Annotated[Session, Depends(get_db)],
    _authorized_user: Annotated[
        AppUser, Depends(require_permission("roles.permissions.update"))
    ],
) -> RoleResponse:
    return service.set_role_permissions(session, role_id, request)


@router.patch("/{role_id}/deactivate", response_model=RoleResponse)
def deactivate_role(
    role_id: Annotated[int, Path(ge=1, le=2**63 - 1)],
    session: Annotated[Session, Depends(get_db)],
    _authorized_user: Annotated[
        AppUser, Depends(require_permission("roles.deactivate"))
    ],
) -> RoleResponse:
    return service.deactivate_role(session, role_id)
