from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.mixins import IdMixin


class BackgroundJob(IdMixin, Base):
    __tablename__ = "background_job"
    __table_args__ = (
        CheckConstraint(
            "progress_percent IS NULL OR progress_percent BETWEEN 0 AND 100",
            name="progress_range",
        ),
        CheckConstraint("attempts >= 0", name="nonnegative_attempts"),
    )

    type: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    requested_by_id: Mapped[int] = mapped_column(
        ForeignKey("app_user.id"), nullable=False
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    result_file_id: Mapped[int | None] = mapped_column(
        ForeignKey("stored_file.id"), unique=True
    )
    error_code: Mapped[str | None] = mapped_column(String(80))
    progress_percent: Mapped[int | None] = mapped_column(SmallInteger)
    attempts: Mapped[int] = mapped_column(server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    outbox_message: Mapped["OutboxMessage | None"] = relationship(uselist=False)


class OutboxMessage(IdMixin, Base):
    __tablename__ = "outbox_message"
    __table_args__ = (CheckConstraint("attempts >= 0", name="nonnegative_attempts"),)

    job_id: Mapped[int] = mapped_column(
        ForeignKey("background_job.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(server_default="0", nullable=False)
