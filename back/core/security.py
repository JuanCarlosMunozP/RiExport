from datetime import datetime,timedelta, timezone
from typing import Any

from dotenv import load_dotenv
from passlib.context import CryptContext

from jose import JWTError,jwt


from core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")


def hash_password(plain:str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain:str,hashed:str) -> bool:
    return pwd_context.verify(plain,hashed)


settings = get_settings()

def create_access_token(subject: str | int, expires_delta:timedelta | None = None) -> str:

    expire = datetime.now(tz=timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub":str(subject), "exp":expire,"type":"access"}
    return jwt.encode(payload,settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(subject:str | int) -> str:
    expire = datetime.now(tz=timezone.utc) + timedelta(settings.REFRESH_TOKEN_EXPIRE_MINTES)
    payload = {"sub":str(subject),"exp":expire,"type":"refresh"}
    return jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

def decode_token(token:str) -> dict[str,Any]:
    try:
        return jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
    except JWTError:
        raise ValueError(f"Invalid Token")
