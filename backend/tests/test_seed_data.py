from unittest.mock import Mock

from sqlalchemy.dialects import postgresql

from scripts.seed_data import (
    ADMIN_PERMISSION_CODES,
    CERTIFICATIONS,
    PERMISSIONS,
    ROLES,
    UNITS,
    seed_reference_data,
)


def test_seed_includes_only_approved_reference_catalog_values() -> None:
    assert [row["code"] for row in UNITS] == ["kg", "t"]
    assert [row["code"] for row in CERTIFICATIONS] == [
        "ORGANIC",
        "FAIR_TRADE",
        "RAINFOREST_ALLIANCE",
    ]
    assert [row["name"] for row in ROLES] == [
        "administrador",
        "usuario_comercial",
        "encargado_logistico",
        "cliente",
    ]


def test_seed_uses_do_nothing_conflicts_and_returns_insert_counts() -> None:
    session = Mock()
    session.scalar.return_value = None
    session.execute.side_effect = [
        Mock(all=Mock(return_value=[(1,), (2,), (3,), (4,)])),
        Mock(all=Mock(return_value=[(code,) for code in ADMIN_PERMISSION_CODES])),
        Mock(all=Mock(return_value=[(1,), (2,)])),
        Mock(all=Mock(return_value=[(1,), (2,), (3,)])),
    ]

    inserted = seed_reference_data(session)

    assert inserted == {
        "unit_of_measure": 2,
        "certification": 3,
        "role": 4,
        "permission": len(PERMISSIONS),
        "role_permission": 0,
    }
    assert session.execute.call_count == 4
    for call in session.execute.call_args_list:
        statement = call.args[0]
        sql = str(statement.compile(dialect=postgresql.dialect()))
        assert "ON CONFLICT (" in sql
        assert "DO NOTHING" in sql
