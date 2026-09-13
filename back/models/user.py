from datetime import datetime
from typing import Optional

from pydantic import field_validator, validator
from sqlalchemy import Boolean,Column, DateTime,Integer, String,Date
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

    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    name: Mapped[str] = mapped_column(String(150),nullable=True)
    email:Mapped[str] = mapped_column(String(150),unique=True,index=True)
    password: Mapped[str] = mapped_column(String(150),unique=True,index=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum)
    is_active: Mapped[bool] = mapped_column(Boolean,default=True)

 