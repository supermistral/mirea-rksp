import datetime

import sqlalchemy as sa
from sqlalchemy.orm import validates
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from db import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(sa.String(128))
    quantity: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=datetime.datetime.now,
    )
    completed: Mapped[bool] = mapped_column(default=False)

    @validates("quantity")
    def validate_quantity(self, key: str, value: int) -> int:
        if value < 0:
            raise ValueError("Quantity must be a positive number")
        return value
