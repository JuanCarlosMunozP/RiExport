from datetime import timedelta,datetime

from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy import exists

from core.security import create_access_token, create_password_reset_token, get_password_hash, verify_password, verify_password_reset_token
from db.session import get_db
from sqlalchemy.orm import Session
from models import User
from schemas.token import ForgotPasswordRequest, LoginRequest, PasswordResetResponse, PasswordResetSuccessResponse, ResetPasswordRequest, Token
from schemas.user import UserCreate, UserResponse


router = APIRouter()

@router.post("/signup",response_model=UserResponse)
def signup(user:UserCreate, db:Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()


    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )
    else:
        print("Usuario creado exitosamente")

    hashed_password = get_password_hash(user.password)

    if not user.password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
        )

  
    db_user = User(
        email=user.email,
        name=user.name,
        password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(db_user)

    setattr(db_user,"welcome_message",f"Welcome to the platform, {db_user.name}!")

@router.post("/login",response_model=Token)
async def login(login_data:LoginRequest,db:Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not verify_password(login_data.password,user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    
    return {
        "message":"Login successfully",
        "welcome_message":f"Welcome back, {user.name}",
        "token_type":"bearer"
    }

@router.post("/forgot-password",response_model=PasswordResetResponse)
def forgot_password(request:ForgotPasswordRequest, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with this email address",
        )

    reset_token = create_password_reset_token(user.email)

    user.reset_token = reset_token 
    user.reset_token_expires = datetime.utcnow()
    db.commit()

    return {
        "message":f"Password reset token has been generated and sent to {user.email}",
    }

@router.post("/reset-password",response_model=PasswordResetSuccessResponse)
def reset_password(request: ResetPasswordRequest,db:Session = Depends(get_db)):

    try:
        email = verify_password_reset_token(request.token)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )

        user = db.query(User).filter(
            User.email == email,
            User.reset_token == request.token,
            User.reset_token_expires > datetime.utcnow()
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )

        user.password = get_password_hash(request.new_password)
        user.reset_token = None
        user.reset_token_expires = None

        db.commit()
        return PasswordResetSuccessResponse(message="Password has been sucessfully reset")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error ocurred while resetting password"
        ) from e