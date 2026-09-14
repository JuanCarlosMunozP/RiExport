import logging

from fastapi import APIRouter, Depends, Form, HTTPException,status
from datetime import timedelta,datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from schemas.auth import RefreshRequest, TokenPair, UserCreate, UserResponse
from core.security import create_access_token, create_refresh_token, decode_token, hash_password,verify_password
from db.session import get_db
from models import User, UserRole


router = APIRouter()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def register(payload:UserCreate, db:Session = Depends(get_db)) -> User:
    user_exists = db.execute(
        select(User).where(User.username == payload.username)
    ).scalar_one_or_none()
    if user_exists:
        raise HTTPException(status_code=401,detail="Username already exists")

    email_exists = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()
    if email_exists:
        raise HTTPException(status_code=401,detail="Email already exists")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()
    logger.info("Registro Exitoso")
    db.refresh(user)
    return user

@router.post("/login",response_model=TokenPair)
def login(
    username: str = Form(),
    password: str = Form(),
    db: Session = Depends(get_db),
) -> TokenPair:
    result = db.execute(
        select(User).where((User.username == username) | (User.email == username))
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(password,user.hashed_password):
        raise HTTPException(status_code=401,detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403,detail="User is inactive")

    if user.id is None:
        raise HTTPException(status_code=500,detail="User not found")

    logger.info("Inicio de Sesion exitoso")

    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id)
    )

@router.post("/refresh",response_model=TokenPair)
def refresh(payload:RefreshRequest) -> TokenPair:

    try:
        claims = decode_token(payload.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401,detail=str(e)) from e

    if claims.get("type") != "refresh":
        raise HTTPException(status_code=401,detail="Wrong token type")

    user_id = claims["sub"]

    return TokenPair(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )