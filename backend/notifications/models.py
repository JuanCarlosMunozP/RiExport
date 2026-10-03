from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.mixins import IdMixin

if TYPE_CHECKING:
    from users.models import AppUser


class Notification(IdMixin, Base):
    __tablename__ = "notification"
    __table_args__ = (
        CheckConstraint(
            "(type = 'low_stock' AND product_lot_id IS NOT NULL AND payment_obligation_id IS NULL) "
            "OR (type = 'payment_due' AND payment_obligation_id IS NOT NULL AND product_lot_id IS NULL)",
            name="type_target_match",
        ),
        Index(
            "ix_notification_recipient_read_created",
            "recipient_user_id",
            "read_at",
            "created_at",
        ),
    )

    recipient_user_id: Mapped[int] = mapped_column(
        ForeignKey("app_user.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    product_lot_id: Mapped[int | None] = mapped_column(ForeignKey("product_lot.id"))
    payment_obligation_id: Mapped[int | None] = mapped_column(
        ForeignKey("payment_obligation.id")
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    body: Mapped[str] = mapped_column(String(500), nullable=False)
    dedupe_key: Mapped[str | None] = mapped_column(String(180), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    recipient: Mapped["AppUser"] = relationship()
