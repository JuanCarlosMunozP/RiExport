from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.mixins import IdMixin

if TYPE_CHECKING:
    from orders.models import CustomerOrder
    from products.models import Currency


class ExchangeRate(IdMixin, Base):
    __tablename__ = "exchange_rate"
    __table_args__ = (
        CheckConstraint("rate > 0", name="positive_rate"),
        UniqueConstraint(
            "from_currency_code", "to_currency_code", "provider", "observed_at"
        ),
    )

    from_currency_code: Mapped[str] = mapped_column(
        ForeignKey("currency.code"), nullable=False
    )
    to_currency_code: Mapped[str] = mapped_column(
        ForeignKey("currency.code"), nullable=False
    )
    rate: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    from_currency: Mapped["Currency"] = relationship(foreign_keys=[from_currency_code])
    to_currency: Mapped["Currency"] = relationship(foreign_keys=[to_currency_code])


class PaymentObligation(IdMixin, Base):
    __tablename__ = "payment_obligation"
    __table_args__ = (CheckConstraint("amount_due > 0", name="positive_amount_due"),)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("customer_order.id"), nullable=False, index=True
    )
    amount_due: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    currency_code: Mapped[str] = mapped_column(
        ForeignKey("currency.code"), nullable=False
    )
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    order: Mapped["CustomerOrder"] = relationship()
    currency: Mapped["Currency"] = relationship()


class PaymentTransaction(IdMixin, Base):
    __tablename__ = "payment_transaction"
    __table_args__ = (CheckConstraint("amount > 0", name="positive_amount"),)

    obligation_id: Mapped[int] = mapped_column(
        ForeignKey("payment_obligation.id"), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exchange_rate_id: Mapped[int | None] = mapped_column(ForeignKey("exchange_rate.id"))
    recorded_by_id: Mapped[int] = mapped_column(
        ForeignKey("app_user.id"), nullable=False
    )
    obligation: Mapped["PaymentObligation"] = relationship()
    exchange_rate: Mapped["ExchangeRate | None"] = relationship()
