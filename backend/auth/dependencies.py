"""FastAPI dependencies for authenticated requests."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.errors import APIError
from core.security import InvalidAccessToken, decode_access_token
from database.session import get_db
from roles.models import Role, RolePermission
from users.models import AppUser

_bearer_scheme = HTTPBearer(auto_error=False)


def _authentication_error() -> APIError:
    return APIError(
        status_code=401,
        code="UNAUTHORIZED",
        message="Se requiere autenticación válida.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ],
    session: Annotated[Session, Depends(get_db)],
) -> AppUser:
    """Resolve a valid bearer access token to an active database user."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _authentication_error()

    try:
        subject = decode_access_token(credentials.credentials)["sub"]
        user_id = int(subject)
        if user_id < 1 or str(user_id) != subject:
            raise ValueError("Invalid user identifier")
    except (InvalidAccessToken, TypeError, ValueError):
        raise _authentication_error() from None

    user = session.get(AppUser, user_id)
    if user is None or not user.is_active:
        raise _authentication_error()
    return user


CurrentUser = Annotated[AppUser, Depends(get_current_user)]


def require_permission(permission_code: str):
    """Require an active user's active role to grant a specific permission."""

    def permission_dependency(
        current_user: CurrentUser,
        session: Annotated[Session, Depends(get_db)],
    ) -> AppUser:
        permission = session.scalar(
            select(RolePermission.permission_code)
            .join(Role, Role.id == RolePermission.role_id)
            .where(
                RolePermission.role_id == current_user.role_id,
                RolePermission.permission_code == permission_code,
                Role.is_active.is_(True),
            )
        )
        if permission is None:
            raise APIError(
                status_code=403,
                code="FORBIDDEN",
                message="No tienes permiso para esta operación.",
            )
        return current_user

    return permission_dependency
