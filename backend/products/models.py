from decimal import Decimal

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.mixins import IdMixin, TimestampMixin


class Country(Base):
    __tablename__ = "country"

    code: Mapped[str] = mapped_column(CHAR(2), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class Currency(Base):
    __tablename__ = "currency"

    code: Mapped[str] = mapped_column(CHAR(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    minor_units: Mapped[int] = mapped_column(SmallInteger, nullable=False)


class UnitOfMeasure(Base):
    __tablename__ = "unit_of_measure"

    code: Mapped[str] = mapped_column(String(12), primary_key=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False)


class Product(IdMixin, TimestampMixin, Base):
    __tablename__ = "product"
    __table_args__ = (
        CheckConstraint("type IN ('coffee', 'cacao')", name="valid_type"),
        CheckConstraint(
            "low_stock_threshold IS NULL OR low_stock_threshold >= 0",
            name="nonnegative_stock_threshold",
        ),
    )

    type: Mapped[str] = mapped_column(String(10), nullable=False)
    variety: Mapped[str] = mapped_column(String(120), nullable=False)
    quality_grade: Mapped[str] = mapped_column(String(80), nullable=False)
    hs_code: Mapped[str | None] = mapped_column(String(20))
    base_unit_code: Mapped[str] = mapped_column(
        ForeignKey("unit_of_measure.code"), nullable=False
    )
    low_stock_threshold: Mapped[Decimal | None] = mapped_column(Numeric(18, 3))
    is_active: Mapped[bool] = mapped_column(server_default="true", nullable=False)
    coffee_detail: Mapped["CoffeeDetail | None"] = relationship(uselist=False)
    cacao_detail: Mapped["CacaoDetail | None"] = relationship(uselist=False)
    certifications: Mapped[list["ProductCertification"]] = relationship()


class CoffeeDetail(Base):
    __tablename__ = "coffee_detail"
    __table_args__ = (
        CheckConstraint("humidity_percent BETWEEN 0 AND 100", name="humidity_range"),
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE"), primary_key=True
    )
    humidity_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)


class CacaoDetail(Base):
    __tablename__ = "cacao_detail"
    __table_args__ = (
        CheckConstraint(
            "fermentation_percent BETWEEN 0 AND 100", name="fermentation_range"
        ),
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE"), primary_key=True
    )
    bean_type: Mapped[str] = mapped_column(String(100), nullable=False)
    fermentation_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)


class Certification(IdMixin, TimestampMixin, Base):
    __tablename__ = "certification"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(server_default="true", nullable=False)


class ProductCertification(Base):
    __tablename__ = "product_certification"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE"), primary_key=True
    )
    certification_id: Mapped[int] = mapped_column(
        ForeignKey("certification.id", ondelete="CASCADE"), primary_key=True
    )
    certification: Mapped["Certification"] = relationship()
