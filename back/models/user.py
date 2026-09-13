from datetime import datetime
from typing import Optional

from pydantic import field_validator, validator
from sqlalchemy import Boolean,Column, DateTime,Integer, String,Date, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship

from enum import Enum

class UserRole(str,Enum):
    ADMIN = "Administrator"
    USER = "User"
    EXPORT_MANAGER = "Export Manager"
    LOGISTICS_MANAGER = "Logistics Manager"


class Base(DeclarativeBase):
    pass

class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50),unique=True,index=True,nullable=False)
    email:Mapped[str] = mapped_column(String(255),unique=True,index=True,nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(150),nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum)
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),server_default=func.now(),nullable=False
    )

 