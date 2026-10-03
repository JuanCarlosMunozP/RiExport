from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from auth.dependencies import require_permission
from database.session import get_db
from users import service
from users.models import AppUser
from users.schemas import (
    CreateUserRequest,
    UserListResponse,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserListResponse)
def query_users(
    session: Annotated[Session, Depends(get_db)],
    _authorized_user: Annotated[AppUser, Depends(require_permission("users.read"))],
    q: Annotated[str | None, Query(max_length=100)] = None,
    role_id: Annotated[int | None, Query(ge=1, le=2**63 - 1)] = None,
    is_active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> UserListResponse:
    return service.list_users(
        session,
        query=q,
        role_id=role_id,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    request: CreateUserRequest,
    session: Annotated[Session, Depends(get_db)],
    _authorized_user: Annotated[AppUser, Depends(require_permission("users.create"))],
) -> AppUser:
    return service.create_user(session, request)
