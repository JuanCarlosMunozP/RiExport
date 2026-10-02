from pydantic import BaseModel, Field


class Pagination(BaseModel):
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
    total: int = Field(ge=0)


class PaginatedResponse[ItemT](BaseModel):
    items: list[ItemT]
    pagination: Pagination


class ErrorDetail(BaseModel):
    field: str | None = None
    code: str
    message: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorPayload
