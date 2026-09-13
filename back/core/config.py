from pydantic import BaseModel
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):

    PROJECT_NAME: str = "Authentication API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = os.getenv("DATABASE_URL","postgresql://postgres:postgres@localhost:5432/RiDB")

    if not DATABASE_URL:
        print("Error al conectar al conectar a la db, DATABASE_URL not found")

    SECRET_KEY: str = os.getenv("SECRET_KEY","tUewkF2sGo8ACY57k9O55R8icxlpXZAsJblt6bodtA=")

    if not SECRET_KEY:
        print("Not found secrety key")
        
    ALGORITHM: str = os.getenv("ALGORITHM","HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","30"))

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
