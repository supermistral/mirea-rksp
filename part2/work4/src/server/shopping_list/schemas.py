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
        from_attributes = True


class ProductCreate(BaseModel):
    text: str
    quantity: Optional[int] = Field(None, gt=0)
    completed: Optional[bool] = None


class ProductUpdate(BaseModel):
    id: int
    text: Optional[str] = None
    quantity: Optional[int] = Field(None, gt=0)
    completed: Optional[bool] = None
