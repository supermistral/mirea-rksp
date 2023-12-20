from typing import Optional
from datetime import datetime

from server.shopping_list.models import Product


def create_product_from_db(
    id: int,
    text: str,
    quantity: Optional[int] = None,
    created_at: Optional[datetime] = None,
    completed: Optional[bool] = None,
) -> Product:
    kw = {
        "id": id,
        "text": text,
        "quantity": quantity or 1,
        "created_at": created_at or datetime(year=2000, month=1, day=1),
        "completed": completed or False,
    }
    return Product(**kw)
