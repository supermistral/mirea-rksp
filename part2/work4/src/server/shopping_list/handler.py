import asyncio
from typing import Optional

import reactivex
import reactivex.operators as ops
from reactivestreams.publisher import Publisher
from reactivestreams.subscriber import Subscriber
from rsocket.helpers import create_future
from rsocket.payload import Payload
from rsocket.request_handler import BaseRequestHandler

from tooling import api
from .repository import ProductRepository
from .streams import ProductCreatingSubscriber, ProductGettingPublisher
from .streams import ProductCreatingPublisher


with_product_repository = api.with_repository(ProductRepository)


class Handler(BaseRequestHandler):
    @with_product_repository
    async def request_response(self, payload: Payload, repo: ProductRepository) -> asyncio.Future:
        data = api.load_data(payload.data)
        product_id = data["id"]

        product = await repo.get(product_id)
        encoded_product = api.dump_data(product)

        return create_future(Payload(encoded_product))

    @with_product_repository
    async def request_fire_and_forget(self, payload: Payload, repo: ProductRepository):
        data = api.load_data(payload.data)
        product_id = data["id"]

        await repo.set_completed(product_id, completed=True)

    async def request_channel(self, payload: Payload) -> tuple[Optional[Publisher], Optional[Subscriber]]:
        data = api.load_data(payload.data)

        publisher = reactivex.create(ProductCreatingPublisher())

    async def request_stream(self, payload: Payload) -> Publisher:
        data = api.load_data(payload.data)
        count = data["count"]

        publisher = reactivex.create(ProductGettingPublisher(count))

        return publisher
