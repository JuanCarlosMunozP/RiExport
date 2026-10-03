from typing import TYPE_CHECKING

from sqlalchemy import CHAR, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.mixins import IdMixin, TimestampMixin

if TYPE_CHECKING:
    from farms.models import Farm
    from products.models import Country


class Supplier(IdMixin, TimestampMixin, Base):
    __tablename__ = "supplier"

    business_name: Mapped[str] = mapped_column(String(180), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(160))
    email: Mapped[str | None] = mapped_column(String(254))
    phone: Mapped[str | None] = mapped_column(String(32))
    country_code: Mapped[str] = mapped_column(
        CHAR(2), ForeignKey("country.code"), nullable=False
    )
    address: Mapped[str | None] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(server_default="true", nullable=False)
    country: Mapped["Country"] = relationship()
    farms: Mapped[list["Farm"]] = relationship()
