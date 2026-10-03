from unittest.mock import Mock

from sqlalchemy.dialects import postgresql

from scripts.seed_data import CERTIFICATIONS, ROLES, UNITS, seed_reference_data


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
    session.execute.side_effect = [
        Mock(all=Mock(return_value=[(1,), (2,)])),
        Mock(all=Mock(return_value=[(1,), (2,), (3,)])),
        Mock(all=Mock(return_value=[(1,), (2,), (3,), (4,)])),
    ]

    inserted = seed_reference_data(session)

    assert inserted == {"unit_of_measure": 2, "certification": 3, "role": 4}
    assert session.execute.call_count == 3
    for call in session.execute.call_args_list:
        statement = call.args[0]
        sql = str(statement.compile(dialect=postgresql.dialect()))
        assert "ON CONFLICT (" in sql
        assert "DO NOTHING" in sql
