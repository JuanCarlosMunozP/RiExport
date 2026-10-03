from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import service
from auth.schemas import LoginRequest, TokenResponse
from database.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    session: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    return service.login(session, request)
