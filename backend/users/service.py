"""User administration use cases."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.errors import APIError
from core.responses import PaginatedResponse
from core.security import hash_password
from users import repository
from users.models import AppUser
from users.schemas import CreateUserRequest, UpdateUserRequest, UserResponse


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


def update_user(
    session: Session,
    user_id: int,
    request: UpdateUserRequest,
) -> AppUser:
    user = repository.get_user(session, user_id)
    if user is None:
        raise _user_not_found()

    changes = request.model_dump(exclude_unset=True)
    email = changes.get("email")
    if email is not None:
        normalized_email = str(email)
        if repository.email_exists_for_other_user(session, normalized_email, user_id):
            raise _duplicate_email_error()
        changes["email"] = normalized_email

    role_id = changes.get("role_id")
    if role_id is not None:
        role = repository.get_role(session, role_id)
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
        if (
            user.is_active
            and role_id != user.role_id
            and _is_administrator(session, user.role_id)
        ):
            _ensure_another_active_administrator(session, user.role_id)

    for field, value in changes.items():
        setattr(user, field, value)
    try:
        session.commit()
        session.refresh(user)
    except IntegrityError:
        session.rollback()
        if email is not None and repository.email_exists_for_other_user(
            session, str(email), user_id
        ):
            raise _duplicate_email_error() from None
        raise
    return user


def deactivate_user(session: Session, user_id: int, actor_id: int) -> AppUser:
    if user_id == actor_id:
        raise APIError(
            status_code=409,
            code="CONFLICT",
            message="No puedes desactivar tu propio usuario.",
        )
    user = repository.get_user(session, user_id)
    if user is None:
        raise _user_not_found()
    if not user.is_active:
        return user
    if _is_administrator(session, user.role_id):
        _ensure_another_active_administrator(session, user.role_id)
    user.is_active = False
    session.commit()
    session.refresh(user)
    return user


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


def _user_not_found() -> APIError:
    return APIError(
        status_code=404,
        code="NOT_FOUND",
        message="No se encontró el usuario solicitado.",
    )


def _is_administrator(session: Session, role_id: int) -> bool:
    role = repository.get_role(session, role_id)
    return role is not None and role.name.strip().casefold() == "administrador"


def _ensure_another_active_administrator(session: Session, role_id: int) -> None:
    if repository.count_active_users_with_role(session, role_id) <= 1:
        raise APIError(
            status_code=409,
            code="CONFLICT",
            message="No se puede dejar el sistema sin un administrador activo.",
        )
