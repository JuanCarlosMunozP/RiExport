from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.security import decode_token
from db.session import get_db
from models.user import User


oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token:str = Depends(oauth2_schema),db:Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"},
    )
    try:
        claims = decode_token(token)
    except ValueError as e:
        raise credentials_error from e

    if claims.get("type") != "access":
        raise credentials_error

    user_id = claims.get("sub")
    if not user_id:
        raise credentials_error

    user = db.get(User,int(user_id))
    if not user or not user.is_active:
        raise credentials_error
    return user