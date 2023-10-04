from typing import Sequence

from sqlalchemy import select
from sqlalchemy import delete
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

    async def get(self, id_: int) -> Product:
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
        product = Product(**schema.dict(exclude_unset=True))

        self.db_session.add(product)
        await self._maybe_commit()

        return product

    async def update(self, schema: ProductUpdateSchema) -> Product:
        product = await self.get(schema.id)

        for key, value in schema.dict(exclude_unset=True).items():
            setattr(product, key, value)

        await self._maybe_commit()

        return product

    async def delete(self, id_: int) -> None:
        await self.db_session.execute(
            delete(Product).where(Product.id == id_)
        )
        await self._maybe_commit()

    async def set_completed(self, id_: int, completed: bool) -> Product:
        product = await self.get(id_)

        product.completed = True
        await self._maybe_commit()

        return product

    async def all_uncompleted(self, limit: int = 100) -> Sequence[Product]:
        result = await self.db_session.execute(
            select(Product).filter(Product.completed == False).limit(limit)
        )
        return result.scalars().all()

    async def _maybe_commit(self):
        if self.commit_on_execution:
            await self.db_session.commit()
