"""Insert approved baseline catalog data into PostgreSQL."""

from collections.abc import Sequence
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from database.session import get_session_factory
from products.models import Certification, UnitOfMeasure

UNITS: Sequence[dict[str, Any]] = (
    {"code": "kg", "name": "Kilogramo"},
    {"code": "t", "name": "Tonelada métrica"},
)

CERTIFICATIONS: Sequence[dict[str, Any]] = (
    {"code": "ORGANIC", "name": "Orgánico"},
    {"code": "FAIR_TRADE", "name": "Fair Trade"},
    {"code": "RAINFOREST_ALLIANCE", "name": "Rainforest Alliance"},
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
    )
    result = session.execute(statement)
    return result.rowcount or 0


def seed_reference_data(session: Session) -> dict[str, int]:
    """Insert missing reference rows without updating existing catalog values."""
    return {
        "unit_of_measure": _insert_missing(session, UnitOfMeasure, UNITS, ("code",)),
        "certification": _insert_missing(
            session, Certification, CERTIFICATIONS, ("code",)
        ),
    }


def main() -> None:
    session_factory = get_session_factory()
    with session_factory.begin() as session:
        inserted = seed_reference_data(session)

    print(
        "Datos semilla insertados: "
        f"{inserted['unit_of_measure']} unidades, "
        f"{inserted['certification']} certificaciones."
    )


if __name__ == "__main__":
    main()
