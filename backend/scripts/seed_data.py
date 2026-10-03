"""Insert approved baseline catalog data into PostgreSQL."""

import argparse
from collections.abc import Sequence
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

import database.models  # noqa: F401
from database.session import get_session_factory
from products.models import Certification, UnitOfMeasure
from roles.models import Role

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
    return {
        "unit_of_measure": _insert_missing(session, UnitOfMeasure, UNITS, ("code",)),
        "certification": _insert_missing(
            session, Certification, CERTIFICATIONS, ("code",)
        ),
        "role": seed_roles(session),
    }


def seed_roles(session: Session) -> int:
    """Insert the agreed system roles without assigning permissions."""
    return _insert_missing(session, Role, ROLES, ("name",))


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga datos de referencia RiExport.")
    parser.add_argument(
        "--roles-only",
        action="store_true",
        help="Inserta únicamente los roles del sistema.",
    )
    args = parser.parse_args()

    session_factory = get_session_factory()
    with session_factory.begin() as session:
        inserted = (
            {"role": seed_roles(session)}
            if args.roles_only
            else seed_reference_data(session)
        )

    summary = ", ".join(f"{count} {name}" for name, count in inserted.items())
    print(f"Datos semilla insertados: {summary}.")


if __name__ == "__main__":
    main()
