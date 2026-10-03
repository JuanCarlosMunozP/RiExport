from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.mixins import IdMixin

if TYPE_CHECKING:
    from farms.models import ProductLot


class InventoryMovement(IdMixin, Base):
    __tablename__ = "inventory_movement"
    __table_args__ = (
        CheckConstraint("quantity_delta <> 0", name="nonzero_quantity_delta"),
        CheckConstraint(
            "NOT (order_line_id IS NOT NULL AND export_line_id IS NOT NULL)",
            name="single_source",
        ),
        Index("ix_inventory_movement_lot_occurred", "product_lot_id", "occurred_at"),
    )

    product_lot_id: Mapped[int] = mapped_column(
        ForeignKey("product_lot.id"), nullable=False
    )
    quantity_delta: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    reason: Mapped[str] = mapped_column(String(30), nullable=False)
    order_line_id: Mapped[int | None] = mapped_column(ForeignKey("order_line.id"))
    export_line_id: Mapped[int | None] = mapped_column(ForeignKey("export_line.id"))
    performed_by_id: Mapped[int] = mapped_column(
        ForeignKey("app_user.id"), nullable=False
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    note: Mapped[str | None] = mapped_column(String(300))
    product_lot: Mapped["ProductLot"] = relationship()
