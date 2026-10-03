from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.mixins import IdMixin, TimestampMixin

if TYPE_CHECKING:
    from documents.models import StoredFile
    from roles.models import Role


class AppUser(IdMixin, TimestampMixin, Base):
    __tablename__ = "app_user"

    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32))
    role_id: Mapped[int] = mapped_column(
        ForeignKey("role.id"), nullable=False, index=True
    )
    photo_file_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "stored_file.id",
            use_alter=True,
            name="fk_app_user_photo_file_id_stored_file",
        ),
        unique=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )
    role: Mapped["Role"] = relationship()
    photo_file: Mapped["StoredFile | None"] = relationship(foreign_keys=[photo_file_id])


class PasswordResetToken(IdMixin, Base):
    __tablename__ = "password_reset_token"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("app_user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    user: Mapped["AppUser"] = relationship()
