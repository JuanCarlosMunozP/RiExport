from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    Date,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    SmallInteger,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.mixins import IdMixin, TimestampMixin

if TYPE_CHECKING:
    from farms.models import ProductLot
    from orders.models import CustomerOrder, OrderLine
    from products.models import Country


class Incoterm(Base):
    __tablename__ = "incoterm"

    code: Mapped[str] = mapped_column(String(8), primary_key=True)
    edition_year: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class Export(IdMixin, TimestampMixin, Base):
    __tablename__ = "export"
    __table_args__ = (
        ForeignKeyConstraint(
            ["incoterm_code", "incoterm_year"],
            ["incoterm.code", "incoterm.edition_year"],
        ),
        Index("ix_export_order_date", "order_id", "export_date"),
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("customer_order.id"), nullable=False
    )
    destination_country_code: Mapped[str] = mapped_column(
        CHAR(2), ForeignKey("country.code"), nullable=False
    )
    incoterm_code: Mapped[str] = mapped_column(String(8), nullable=False)
    incoterm_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    export_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("app_user.id"), nullable=False
    )
    order: Mapped["CustomerOrder"] = relationship()
    destination_country: Mapped["Country"] = relationship()
    incoterm: Mapped["Incoterm"] = relationship()
    lines: Mapped[list["ExportLine"]] = relationship()


class ExportLine(IdMixin, Base):
    __tablename__ = "export_line"
    __table_args__ = (CheckConstraint("quantity > 0", name="positive_quantity"),)

    export_id: Mapped[int] = mapped_column(
        ForeignKey("export.id"), nullable=False, index=True
    )
    order_line_id: Mapped[int] = mapped_column(
        ForeignKey("order_line.id"), nullable=False
    )
    product_lot_id: Mapped[int] = mapped_column(
        ForeignKey("product_lot.id"), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    hs_code_snapshot: Mapped[str] = mapped_column(String(20), nullable=False)
    order_line: Mapped["OrderLine"] = relationship()
    product_lot: Mapped["ProductLot"] = relationship()
