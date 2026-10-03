from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.mixins import IdMixin, TimestampMixin

if TYPE_CHECKING:
    from customers.models import Customer
    from products.models import Currency, Product
    from users.models import AppUser


class CustomerOrder(IdMixin, TimestampMixin, Base):
    __tablename__ = "customer_order"
    __table_args__ = (
        Index("ix_customer_order_customer_status", "customer_id", "status"),
    )

    order_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("app_user.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    currency_code: Mapped[str] = mapped_column(
        ForeignKey("currency.code"), nullable=False
    )
    customer: Mapped["Customer"] = relationship()
    created_by: Mapped["AppUser"] = relationship()
    currency: Mapped["Currency"] = relationship()
    lines: Mapped[list["OrderLine"]] = relationship()


class OrderLine(IdMixin, Base):
    __tablename__ = "order_line"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="positive_quantity"),
        CheckConstraint("unit_price >= 0", name="nonnegative_unit_price"),
        Index("ix_order_line_product", "product_id"),
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("customer_order.id"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    product: Mapped["Product"] = relationship()
