"""User request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from core.responses import PaginatedResponse
from core.security import BCRYPT_MAX_PASSWORD_BYTES


class CreateUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=32)
    role_id: int = Field(ge=1, le=2**63 - 1)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if "\x00" in value:
            raise ValueError("La contraseña no puede contener bytes nulos.")
        if len(value.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
            raise ValueError("La contraseña supera el límite de 72 bytes UTF-8.")
        return value

    @field_validator("first_name", "last_name")
    @classmethod
    def normalize_names(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Este campo es obligatorio.")
        return value

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None
    role_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


UserListResponse = PaginatedResponse[UserResponse]
