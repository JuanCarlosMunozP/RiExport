"""User persistence queries."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from roles.models import Role
from users.models import AppUser


def email_exists(session: Session, email: str) -> bool:
    statement = select(AppUser.id).where(func.lower(AppUser.email) == email)
    return session.scalar(statement) is not None


def get_role(session: Session, role_id: int) -> Role | None:
    return session.get(Role, role_id)


def get_user(session: Session, user_id: int) -> AppUser | None:
    return session.get(AppUser, user_id)


def email_exists_for_other_user(session: Session, email: str, user_id: int) -> bool:
    statement = select(AppUser.id).where(
        func.lower(AppUser.email) == email,
        AppUser.id != user_id,
    )
    return session.scalar(statement) is not None


def count_active_users_with_role(session: Session, role_id: int) -> int:
    statement = (
        select(func.count())
        .select_from(AppUser)
        .where(
            AppUser.role_id == role_id,
            AppUser.is_active.is_(True),
        )
    )
    return session.scalar(statement) or 0


def add_user(session: Session, user: AppUser) -> AppUser:
    session.add(user)
    session.flush()
    session.refresh(user)
    return user


def list_users(
    session: Session,
    *,
    query: str | None,
    role_id: int | None,
    is_active: bool | None,
    limit: int,
    offset: int,
) -> tuple[list[AppUser], int]:
    filters = []
    if query:
        escaped_query = (
            query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        )
        pattern = f"%{escaped_query}%"
        filters.append(
            or_(
                AppUser.email.ilike(pattern, escape="\\"),
                AppUser.first_name.ilike(pattern, escape="\\"),
                AppUser.last_name.ilike(pattern, escape="\\"),
            )
        )
    if role_id is not None:
        filters.append(AppUser.role_id == role_id)
    if is_active is not None:
        filters.append(AppUser.is_active.is_(is_active))

    total = (
        session.scalar(select(func.count()).select_from(AppUser).where(*filters)) or 0
    )
    users = session.scalars(
        select(AppUser)
        .where(*filters)
        .order_by(AppUser.created_at.desc(), AppUser.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return users, total
