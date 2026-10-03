from decimal import Decimal

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from database.mixins import IdMixin, TimestampMixin


class Farm(IdMixin, TimestampMixin, Base):
    __tablename__ = "farm"
    __table_args__ = (
        CheckConstraint(
            "latitude IS NULL OR latitude BETWEEN -90 AND 90", name="latitude_range"
        ),
        CheckConstraint(
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
            name="longitude_range",
        ),
    )

    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("supplier.id"), nullable=False, index=True
    )
    country_code: Mapped[str] = mapped_column(
        CHAR(2), ForeignKey("country.code"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    address: Mapped[str | None] = mapped_column(String(300))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    is_active: Mapped[bool] = mapped_column(server_default="true", nullable=False)


class ProductLot(IdMixin, Base):
    __tablename__ = "product_lot"
    __table_args__ = (
        UniqueConstraint("farm_id", "lot_code"),
        Index("ix_product_lot_farm_product", "farm_id", "product_id"),
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id"), nullable=False, index=True
    )
    farm_id: Mapped[int] = mapped_column(ForeignKey("farm.id"), nullable=False)
    lot_code: Mapped[str] = mapped_column(String(80), nullable=False)
