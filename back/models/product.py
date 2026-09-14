from enum import Enum

from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import Enum as SQLEnum, Integer
from sqlalchemy import String

class TypeProduct(str,Enum):

    COFFEE = "Cafe"
    CACAO = "Cacao"

class Base(DeclarativeBase):

    pass


class Product(Base):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50),unique=True,index=True,nullable=False)
    presentation: Mapped[str] = mapped_column(String(150),index=True,nullable=False)
    stock: Mapped[int] = mapped_column(Integer,index=True,nullable=False)
    type: Mapped[TypeProduct] = mapped_column(SQLEnum)


