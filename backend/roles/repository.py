"""Role and permission persistence queries."""

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from roles.models import Permission, Role, RolePermission
from users.models import AppUser


def list_roles(session: Session, *, include_inactive: bool) -> list[Role]:
    statement = select(Role).options(selectinload(Role.permissions))
    if not include_inactive:
        statement = statement.where(Role.is_active.is_(True))
    return list(session.scalars(statement.order_by(func.lower(Role.name))).all())


def get_role(session: Session, role_id: int) -> Role | None:
    return session.get(Role, role_id)


def get_role_by_name(session: Session, name: str) -> Role | None:
    statement = select(Role).where(func.lower(Role.name) == name)
    return session.scalars(statement).first()


def list_permissions(session: Session) -> list[Permission]:
    return list(session.scalars(select(Permission).order_by(Permission.code)).all())


def get_permissions_by_codes(session: Session, codes: list[str]) -> list[Permission]:
    if not codes:
        return []
    statement = select(Permission).where(Permission.code.in_(codes))
    return list(session.scalars(statement).all())


def add_role(session: Session, role: Role) -> Role:
    session.add(role)
    session.flush()
    return role


def replace_role_permissions(
    session: Session, role_id: int, permission_codes: list[str]
) -> None:
    session.execute(delete(RolePermission).where(RolePermission.role_id == role_id))
    session.add_all(
        [
            RolePermission(role_id=role_id, permission_code=code)
            for code in permission_codes
        ]
    )


def active_user_count_for_role(session: Session, role_id: int) -> int:
    statement = (
        select(func.count())
        .select_from(AppUser)
        .where(
            AppUser.role_id == role_id,
            AppUser.is_active.is_(True),
        )
    )
    return session.scalar(statement) or 0
