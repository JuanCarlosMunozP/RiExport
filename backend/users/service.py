"""User administration use cases."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.errors import APIError
from core.responses import PaginatedResponse
from core.security import hash_password
from users import repository
from users.models import AppUser
from users.schemas import CreateUserRequest, UserResponse


def create_user(session: Session, request: CreateUserRequest) -> AppUser:
    email = str(request.email)
    if repository.email_exists(session, email):
        raise _duplicate_email_error()

    role = repository.get_role(session, request.role_id)
    if role is None or not role.is_active:
        raise APIError(
            status_code=422,
            code="VALIDATION_ERROR",
            message="La solicitud contiene datos no válidos.",
            details=[
                {
                    "field": "role_id",
                    "code": "invalid_value",
                    "message": "El rol indicado no existe o está inactivo.",
                }
            ],
        )

    user = AppUser(
        email=email,
        password_hash=hash_password(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        phone=request.phone,
        role_id=role.id,
    )
    try:
        repository.add_user(session, user)
        session.commit()
    except IntegrityError:
        session.rollback()
        if repository.email_exists(session, email):
            raise _duplicate_email_error() from None
        raise APIError(
            status_code=422,
            code="VALIDATION_ERROR",
            message="La solicitud contiene datos no válidos.",
            details=[
                {
                    "field": "role_id",
                    "code": "invalid_value",
                    "message": "El rol indicado ya no está disponible.",
                }
            ],
        ) from None
    return user


def list_users(
    session: Session,
    *,
    query: str | None,
    role_id: int | None,
    is_active: bool | None,
    limit: int,
    offset: int,
) -> PaginatedResponse[UserResponse]:
    normalized_query = query.strip() if query and query.strip() else None
    users, total = repository.list_users(
        session,
        query=normalized_query,
        role_id=role_id,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    return PaginatedResponse[UserResponse](
        items=[UserResponse.model_validate(user) for user in users],
        pagination={"limit": limit, "offset": offset, "total": total},
    )


def _duplicate_email_error() -> APIError:
    return APIError(
        status_code=409,
        code="CONFLICT",
        message="Ya existe un usuario con ese correo electrónico.",
        details=[
            {
                "field": "email",
                "code": "already_exists",
                "message": "El correo electrónico ya está registrado.",
            }
        ],
    )
