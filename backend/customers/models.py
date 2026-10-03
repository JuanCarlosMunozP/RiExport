from typing import TYPE_CHECKING

from sqlalchemy import CHAR, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.mixins import IdMixin, TimestampMixin

if TYPE_CHECKING:
    from products.models import Country, Currency


class Customer(IdMixin, TimestampMixin, Base):
    __tablename__ = "customer"

    name: Mapped[str] = mapped_column(String(180), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(160))
    email: Mapped[str | None] = mapped_column(String(254))
    country_code: Mapped[str] = mapped_column(
        CHAR(2), ForeignKey("country.code"), nullable=False
    )
    eori_number: Mapped[str | None] = mapped_column(String(35), unique=True)
    preferred_currency_code: Mapped[str] = mapped_column(
        CHAR(3), ForeignKey("currency.code"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(server_default="true", nullable=False)
    country: Mapped["Country"] = relationship()
    preferred_currency: Mapped["Currency"] = relationship()
