from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.dependencies import require_permission
from database.session import get_db
from users import service
from users.models import AppUser
from users.schemas import CreateUserRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


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
