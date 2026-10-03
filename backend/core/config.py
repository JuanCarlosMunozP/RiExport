from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "RiExport API"
    app_env: Literal["development", "testing", "production"] = "development"
    api_v1_prefix: str = "/api/v1"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    cors_origins: str = ""
    cors_allow_credentials: bool = False
    database_url: SecretStr | None = None
    jwt_secret_key: SecretStr | None = None
    jwt_access_token_expire_minutes: int = Field(default=30, gt=0)
    jwt_issuer: str = Field(default="riexport-api", min_length=1)

    @property
    def debug(self) -> bool:
        return self.app_env == "development"

    @property
    def api_docs_enabled(self) -> bool:
        return self.app_env != "production"

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def cors_origin_regex(self) -> str | None:
        if self.app_env == "development":
            return r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
        return None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
