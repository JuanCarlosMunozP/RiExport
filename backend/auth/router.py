from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import service
from auth.schemas import (
    LoginRequest,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    TokenResponse,
)
from database.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    session: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    return service.login(session, request)


@router.post(
    "/password-reset/request",
    response_model=PasswordResetRequestResponse,
    status_code=202,
)
def request_password_reset(
    request: PasswordResetRequest,
    session: Annotated[Session, Depends(get_db)],
) -> PasswordResetRequestResponse:
    return service.request_password_reset(session, request)
