"""Role and permission request and response schemas."""

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CreateRoleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=60)
    description: str | None = Field(default=None, max_length=250)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip().lower().replace(" ", "_")
        if (
            not normalized
            or not normalized[0].isalpha()
            or not all(char.isalnum() or char == "_" for char in normalized)
        ):
            raise ValueError("Usa letras, números y guion bajo en el nombre.")
        return normalized

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value


class UpdateRoleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=2, max_length=60)
    description: str | None = Field(default=None, max_length=250)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().lower().replace(" ", "_")
        if (
            not normalized
            or not normalized[0].isalpha()
            or not all(char.isalnum() or char == "_" for char in normalized)
        ):
            raise ValueError("Usa letras, números y guion bajo en el nombre.")
        return normalized

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value

    @model_validator(mode="after")
    def require_changes(self) -> "UpdateRoleRequest":
        if not self.model_fields_set:
            raise ValueError("Indica al menos un campo para actualizar.")
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("El nombre no puede ser nulo.")
        return self


class SetRolePermissionsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    permission_codes: list[str] = Field(max_length=200)


class PermissionResponse(BaseModel):
    code: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool
    permission_codes: list[str]


class RoleListResponse(BaseModel):
    items: list[RoleResponse]


class PermissionListResponse(BaseModel):
    items: list[PermissionResponse]
