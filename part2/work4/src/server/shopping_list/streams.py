import logging
import time
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from reactivestreams.subscriber import DefaultSubscriber
from reactivestreams.subscriber import Subscription
from rsocket.payload import Payload

from db import get_session
from tooling.api import load_data
from tooling.api import dump_data
from tooling.aio import async_to_sync
from .repository import ProductRepository
from .schemas import ProductCreate

LOG = logging.getLogger(__name__)


class ProductCreatingPublisher:
    def __init__(self, max_count: int):
        self.count = 0
        self.max_count = max_count

    def __call__(self, observer, scheduler):
        pass


class ProductGettingPublisher:
    def __init__(self, limit: int):
        self.limit = limit

    def __call__(self, observer, scheduler):
        with get_session() as session:
            repo = ProductRepository(db_session=session)
            products = repo.all_uncompleted(limit=self.limit)

        for product in products:
            time.sleep(1)

            data = dump_data(product)
            observer.on_next(Payload(data))

        observer.on_completed()


class ProductCreatingSubscriber(DefaultSubscriber):
    def __init__(self):
        self.db_session: Optional[AsyncSession] = None
        self.repo: Optional[ProductRepository] = None
        self._db_session_context = get_session()

    @async_to_sync
    async def on_subscribe(self, subscription: Subscription):
        self.db_session = await self._db_session_context.__aenter__()
        self.repo = ProductRepository(db_session=self.db_session, commit_on_execution=False)

        subscription.request(10)

    @async_to_sync
    async def on_next(self, value, is_complete=False):
        data = load_data(value)
        create_schema = ProductCreate(**data)

        LOG.info(f"[RC] Received data: {data}")
        await self.repo.create(create_schema)

    @async_to_sync
    async def on_complete(self):
        await self._commit()

    @async_to_sync
    async def on_error(self, exception: Exception):
        await self._commit()
        super().on_error(exception=exception)

    async def _commit(self):
        LOG.info("[RC] Commit")

        await self._db_session_context.__aexit__()
        await self.db_session.commit()
