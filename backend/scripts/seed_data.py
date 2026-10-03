"""Insert approved baseline catalog data into PostgreSQL."""

import argparse
from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

import database.models  # noqa: F401
from database.session import get_session_factory
from products.models import Certification, UnitOfMeasure
from roles.models import Permission, Role, RolePermission

UNITS: Sequence[dict[str, Any]] = (
    {"code": "kg", "name": "Kilogramo"},
    {"code": "t", "name": "Tonelada métrica"},
)

CERTIFICATIONS: Sequence[dict[str, Any]] = (
    {"code": "ORGANIC", "name": "Orgánico"},
    {"code": "FAIR_TRADE", "name": "Fair Trade"},
    {"code": "RAINFOREST_ALLIANCE", "name": "Rainforest Alliance"},
)

ROLES: Sequence[dict[str, Any]] = (
    {
        "name": "administrador",
        "description": "Gestiona usuarios, roles y permisos; accede al tablero de KPI.",
    },
    {
        "name": "usuario_comercial",
        "description": "Perfil comercial para las operaciones de productos, clientes, pedidos y exportaciones, según permisos asignados.",
    },
    {
        "name": "encargado_logistico",
        "description": "Perfil logístico para registrar transportista, guía y eventos de envío, según permisos asignados.",
    },
    {
        "name": "cliente",
        "description": "Cliente externo. El acceso debe limitarse a sus propios envíos antes de habilitarlo.",
    },
)

PERMISSIONS: Sequence[dict[str, str]] = (
    {"code": "roles.read", "description": "Consultar roles y permisos."},
    {"code": "roles.create", "description": "Crear roles."},
    {"code": "roles.update", "description": "Editar roles."},
    {
        "code": "roles.permissions.update",
        "description": "Asignar permisos a roles.",
    },
    {"code": "roles.deactivate", "description": "Desactivar roles."},
    {"code": "users.read", "description": "Consultar usuarios."},
    {"code": "users.create", "description": "Registrar usuarios."},
    {"code": "users.update", "description": "Editar usuarios."},
    {"code": "users.deactivate", "description": "Desactivar usuarios."},
)

ADMIN_PERMISSION_CODES = tuple(permission["code"] for permission in PERMISSIONS)


def _insert_missing(
    session: Session,
    model: type,
    rows: Sequence[dict[str, Any]],
    conflict_columns: Sequence[str],
) -> int:
    statement = (
        insert(model)
        .values(rows)
        .on_conflict_do_nothing(index_elements=list(conflict_columns))
        .returning(*model.__table__.primary_key.columns)
    )
    result = session.execute(statement)
    return len(result.all())


def seed_reference_data(session: Session) -> dict[str, int]:
    """Insert missing reference rows without updating existing catalog values."""
    security = seed_security_catalog(session)
    return {
        "unit_of_measure": _insert_missing(session, UnitOfMeasure, UNITS, ("code",)),
        "certification": _insert_missing(
            session, Certification, CERTIFICATIONS, ("code",)
        ),
        **security,
    }


def seed_roles(session: Session) -> int:
    """Insert the agreed system roles without assigning permissions."""
    return _insert_missing(session, Role, ROLES, ("name",))


def seed_security_catalog(session: Session) -> dict[str, int]:
    roles = seed_roles(session)
    permissions = _insert_missing(session, Permission, PERMISSIONS, ("code",))
    role_id = session.scalar(select(Role.id).where(Role.name == "administrador"))
    assignments = 0
    if role_id is not None:
        rows = [
            {"role_id": role_id, "permission_code": code}
            for code in ADMIN_PERMISSION_CODES
        ]
        statement = (
            insert(RolePermission)
            .values(rows)
            .on_conflict_do_nothing(index_elements=["role_id", "permission_code"])
            .returning(*RolePermission.__table__.primary_key.columns)
        )
        assignments = len(session.execute(statement).all())
    return {
        "role": roles,
        "permission": permissions,
        "role_permission": assignments,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga datos de referencia RiExport.")
    parser.add_argument(
        "--roles-only",
        action="store_true",
        help="Inserta roles, permisos del sistema y permisos administrativos.",
    )
    args = parser.parse_args()

    session_factory = get_session_factory()
    with session_factory.begin() as session:
        inserted = (
            seed_security_catalog(session)
            if args.roles_only
            else seed_reference_data(session)
        )

    summary = ", ".join(f"{count} {name}" for name, count in inserted.items())
    print(f"Datos semilla insertados: {summary}.")


if __name__ == "__main__":
    main()
