from pydantic import BaseModel
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):

    PROJECT_NAME: str = "Authentication API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = os.getenv("SECRET_KEY") or ""

    if not SECRET_KEY:
        print("Not found secrety key")


    ALGORITHM: str = os.getenv("ALGORITHM") or "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or "30")
    REFRESH_TOKEN_EXPIRE_MINTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES") or "15")

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
