from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.mixins import IdMixin


class Shipment(IdMixin, Base):
    __tablename__ = "shipment"

    export_id: Mapped[int] = mapped_column(
        ForeignKey("export.id"), nullable=False, index=True
    )
    carrier: Mapped[str] = mapped_column(String(160), nullable=False)
    tracking_number: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    events: Mapped[list["ShipmentEvent"]] = relationship()


class ShipmentEvent(IdMixin, Base):
    __tablename__ = "shipment_event"
    __table_args__ = (
        Index("ix_shipment_event_shipment_occurred", "shipment_id", "occurred_at"),
    )

    shipment_id: Mapped[int] = mapped_column(
        ForeignKey("shipment.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(300))
    recorded_by_id: Mapped[int] = mapped_column(
        ForeignKey("app_user.id"), nullable=False
    )
