from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import configure_mappers
from sqlalchemy.schema import CreateTable

import database.models  # noqa: F401
from database.base import Base

EXPECTED_TABLES = {
    "app_user",
    "audit_log",
    "background_job",
    "cacao_detail",
    "certification",
    "coffee_detail",
    "country",
    "currency",
    "customer",
    "customer_order",
    "exchange_rate",
    "export",
    "export_document",
    "export_line",
    "farm",
    "incoterm",
    "inventory_movement",
    "notification",
    "order_line",
    "outbox_message",
    "password_reset_token",
    "payment_obligation",
    "payment_transaction",
    "permission",
    "product",
    "product_certification",
    "product_lot",
    "role",
    "role_permission",
    "shipment",
    "shipment_event",
    "stored_file",
    "supplier",
    "unit_of_measure",
}


def test_all_er_tables_are_registered_and_compile_for_postgres() -> None:
    configure_mappers()

    assert set(Base.metadata.tables) == EXPECTED_TABLES
    for table in Base.metadata.sorted_tables:
        str(CreateTable(table).compile(dialect=postgresql.dialect()))


def test_composite_and_business_constraints_are_present() -> None:
    assert len(Base.metadata.tables["role_permission"].primary_key.columns) == 2
    assert len(Base.metadata.tables["incoterm"].primary_key.columns) == 2
    assert len(Base.metadata.tables["product_certification"].primary_key.columns) == 2

    movement_checks = {
        constraint.name
        for constraint in Base.metadata.tables["inventory_movement"].constraints
    }
    assert "ck_inventory_movement_nonzero_quantity_delta" in movement_checks
    assert "ck_inventory_movement_single_source" in movement_checks

    notification_checks = {
        constraint.name
        for constraint in Base.metadata.tables["notification"].constraints
    }
    assert "ck_notification_type_target_match" in notification_checks


def test_optional_user_photo_foreign_key_is_deferred_for_cycle() -> None:
    photo_fk = next(
        fk
        for fk in Base.metadata.tables["app_user"].foreign_keys
        if fk.parent.name == "photo_file_id"
    )

    assert photo_fk.use_alter is True
