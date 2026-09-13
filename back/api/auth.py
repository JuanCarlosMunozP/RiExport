from fastapi import APIRouter, Depends, HTTPException,status
from datetime import timedelta,datetime

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from back.schemas.auth import RefreshRequest, TokenPair, UserCreate, UserResponse
from core.security import create_access_token, create_refresh_token, decode_token, hash_password,verify_password
from db.session import get_db
from models import User


router = APIRouter()

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def register(payload:UserCreate, db:AsyncSession = Depends(get_db)) -> User:
    user_exists = await db.execute(
        select(User).where((User.username == payload.username) | (User.email == payload.email))
    )
    if user_exists.scalar_one_or_none():
        raise HTTPException(status_code=403,detail="Username or email already exists.")

    user = User(
        username=payload.username,
        emai=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login",response_model=TokenPair)
async def login(form_data:OAuth2PasswordRequestForm = Depends(),db:AsyncSession = Depends(get_db)) -> TokenPair:
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(status_code=401,detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403,detail="User is inactive")

    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id)
    )

@router.post("/refresh",response_model=TokenPair)
async def refresh(payload:RefreshRequest) -> TokenPair:

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