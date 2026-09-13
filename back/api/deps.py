from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from back.core.security import decode_token
from back.db.session import get_db
from back.models.user import User

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token:str = Depends(oauth2_schema),db:AsyncSession = Depends(get_db)) -> User:
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

    user = await db.get(User,int(user_id))
    if not user or not user.is_active:
        raise credentials_error
    return user