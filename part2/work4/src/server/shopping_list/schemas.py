from typing import Optional
import datetime

from pydantic import BaseModel
from pydantic import Field


class Product(BaseModel):
    id: int
    text: str
    quantity: int
    created_at: datetime.datetime
    completed: bool

    class Config:
        orm_mode = True


class ProductCreate(BaseModel):
    text: str
    quantity: Optional[str] = Field(None, gt=0)
    completed: Optional[bool]


class ProductUpdate(BaseModel):
    id: int
    text: Optional[str]
    quantity: Optional[int] = Field(None, gt=0)
    completed: Optional[bool]
