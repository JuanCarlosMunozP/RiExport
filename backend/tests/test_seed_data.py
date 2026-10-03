from unittest.mock import Mock

from sqlalchemy.dialects import postgresql

from scripts.seed_data import CERTIFICATIONS, UNITS, seed_reference_data


def test_seed_includes_only_approved_reference_catalog_values() -> None:
    assert [row["code"] for row in UNITS] == ["kg", "t"]
    assert [row["code"] for row in CERTIFICATIONS] == [
        "ORGANIC",
        "FAIR_TRADE",
        "RAINFOREST_ALLIANCE",
    ]


def test_seed_uses_do_nothing_conflicts_and_returns_insert_counts() -> None:
    session = Mock()
    session.execute.side_effect = [Mock(rowcount=2), Mock(rowcount=3)]

    inserted = seed_reference_data(session)

    assert inserted == {"unit_of_measure": 2, "certification": 3}
    assert session.execute.call_count == 2
    for call in session.execute.call_args_list:
        statement = call.args[0]
        sql = str(statement.compile(dialect=postgresql.dialect()))
        assert "ON CONFLICT (" in sql
        assert "DO NOTHING" in sql
