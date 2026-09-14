from pydantic import BaseModel, ConfigDict
from enum import Enum

class ProductBase(BaseModel):
    name:str
    presentation:str
    stock: int
    type:Enum


class ProductCreate(ProductBase):
    name:str
    presentation:str
    stock:int
    type:str


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    message_success : str | None = None
    id: int
    name:str
    presentation:str
    stock:str
    type:str