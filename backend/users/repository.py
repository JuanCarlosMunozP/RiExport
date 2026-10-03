"""User persistence queries."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from roles.models import Role
from users.models import AppUser


def email_exists(session: Session, email: str) -> bool:
    statement = select(AppUser.id).where(func.lower(AppUser.email) == email)
    return session.scalar(statement) is not None


def get_role(session: Session, role_id: int) -> Role | None:
    return session.get(Role, role_id)


def add_user(session: Session, user: AppUser) -> AppUser:
    session.add(user)
    session.flush()
    session.refresh(user)
    return user
