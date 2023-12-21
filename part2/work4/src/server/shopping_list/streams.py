import logging
import asyncio
from typing import Optional
from typing import AsyncGenerator
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from reactivestreams.publisher import Publisher
from reactivestreams.subscriber import DefaultSubscriber, Subscriber
from reactivestreams.subscriber import Subscription
from rsocket.payload import Payload
from rsocket.streams.stream_from_async_generator import StreamFromAsyncGenerator

from server.db import get_session
from server.tooling.api import load_data
from server.tooling.aio import async_to_sync
from .repository import ProductRepository
from .schemas import ProductCreate
from .schemas import Product

LOG = logging.getLogger(__name__)


def product_creating_stream(
    limit: int,
    local_subscriber: Optional[Subscriber] = None,
) -> Publisher:
    async def generator() -> AsyncGenerator[tuple[Payload, bool], None]:
        is_complete = False
        time = datetime.utcnow()
        last_added = current_last_added = await _get_first_added_after_time(time)
        counter = 0
        ttl_count = 0
        max_ttl_count = _get_ttl(limit=limit)

        while not is_complete:
            await asyncio.sleep(2)

            current_last_added = await _get_first_added_after_time(time)
            ttl_count += 1

            if ttl_count > max_ttl_count:
                LOG.warning("TTL exceeded, cancel stream")

                yield Payload(None), True
                break

            if (
                current_last_added is not None and last_added is not None
                and current_last_added.id == last_added.id
                or current_last_added == last_added
            ):
                LOG.info("Nothing to send, skip")

                continue

            counter += 1
            is_complete = counter == limit
            last_added = current_last_added

            if current_last_added is not None:
                time = current_last_added.created_at
                data = Product.model_validate(current_last_added, strict=False).model_dump_json().encode("utf-8")
            else:
                data = None

            yield Payload(data), is_complete

    return StreamFromAsyncGenerator(generator=generator)


def product_getting_stream(
    limit: int,
    local_subscriber: Optional[Subscriber] = None,
) -> Publisher:
    async def generator() -> AsyncGenerator[tuple[Payload, bool], None]:
        async with get_session() as session:
            repo = ProductRepository(db_session=session)
            products = await repo.all_uncompleted(limit=limit)

        for idx, product in enumerate(products):
            await asyncio.sleep(1)

            is_complete = idx == len(products) - 1
            data = product.to_json().encode("utf-8")

            yield Payload(data), is_complete

    return StreamFromAsyncGenerator(generator=generator)


class ProductCreatingSubscriber(DefaultSubscriber):
    def __init__(self, limit: int):
        self.limit = limit
        self.db_session: Optional[AsyncSession] = None
        self.repo: Optional[ProductRepository] = None

    @async_to_sync
    async def on_subscribe(self, subscription: Subscription):
        self.subscription = subscription
        subscription.request(self.limit)

    @async_to_sync
    async def on_next(self, value: Payload, is_complete: bool = False):
        data = load_data(value.data)

        LOG.info(f"[RC] Received data: {data}")

        create_schema = ProductCreate(**data)

        async with get_session() as session:
            repo = ProductRepository(db_session=session)
            await repo.create(create_schema)

        if is_complete:
            await self._commit()

    @async_to_sync
    async def on_complete(self):
        await self._commit()

    @async_to_sync
    async def on_error(self, exception: Exception):
        await self._commit()
        super().on_error(exception=exception)

    async def _commit(self):
        LOG.info("[RC] Commit")


def _get_ttl(limit: int) -> int:
    return max(100, limit * 3)


async def _get_first_added_after_time(time: datetime) -> Optional[Product]:
    async with get_session() as session:
        repo = ProductRepository(db_session=session)
        return await repo.get_first_added_after_time(time)
