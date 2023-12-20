from typing import Sequence
from typing import Optional
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Product
from .schemas import (
    ProductCreate as ProductCreateSchema,
    ProductUpdate as ProductUpdateSchema,
)


class ProductRepository:
    def __init__(self, db_session: AsyncSession, commit_on_execution: bool = True):
        self.db_session = db_session
        self.commit_on_execution = commit_on_execution

    async def get(self, id_: int) -> Optional[Product]:
        result = await self.db_session.execute(
            select(Product).filter(Product.id == id_)
        )
        return result.scalar_one_or_none()

    async def all(self) -> Sequence[Product]:
        result = await self.db_session.execute(
            select(Product).order_by(Product.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, schema: ProductCreateSchema) -> Product:
        product = Product(**schema.model_dump(exclude_unset=True, exclude_none=True))

        self.db_session.add(product)
        await self._maybe_commit()

        return product

    async def update(self, schema: ProductUpdateSchema) -> Product:
        product = await self.get(schema.id)

        for key, value in schema.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(product, key, value)

        await self._maybe_commit()

        return product

    async def delete(self, id_: int) -> None:
        await self.db_session.execute(
            delete(Product).where(Product.id == id_)
        )
        await self._maybe_commit()

    async def set_completed(self, id_: int, completed: bool = True) -> Product:
        product = await self.get(id_)

        product.completed = completed
        await self._maybe_commit()

        return product

    async def all_uncompleted(self, limit: int = 100) -> Sequence[Product]:
        result = await self.db_session.execute(
            select(Product)
                .filter(Product.completed == False)
                .order_by(Product.created_at.asc())
                .limit(limit)
        )
        return result.scalars().all()

    async def get_first_added_after_time(self, time: datetime) -> Optional[Product]:
        result = await self.db_session.execute(
            select(Product)
                .filter(Product.created_at > time)
                .order_by(Product.created_at.asc())
                .limit(1)
        )
        return result.scalar_one_or_none()

    async def _maybe_commit(self):
        if self.commit_on_execution:
            await self.db_session.flush()
            await self.db_session.commit()
