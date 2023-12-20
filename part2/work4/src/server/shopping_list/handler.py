from typing import Optional

from reactivestreams.publisher import Publisher
from reactivestreams.subscriber import Subscriber
from rsocket.helpers import create_future
from rsocket.payload import Payload
from rsocket.routing.request_router import RequestRouter
from rsocket.routing.routing_request_handler import RoutingRequestHandler
from rsocket.extensions.composite_metadata import CompositeMetadata

from tooling import api
from .repository import ProductRepository
from .streams import ProductCreatingSubscriber
from .streams import product_creating_stream, product_getting_stream

with_product_repository = api.with_repository(ProductRepository)


def handler_factory():
    router = RequestRouter()

    @router.response("get")
    @with_product_repository
    async def get_response(payload: Payload, composite_metadata: CompositeMetadata, repo: ProductRepository):
        data = api.load_data(payload.data)
        product_id = data["id"]

        product = await repo.get(product_id)
        json = product.to_json() if product else None
        encoded_product = api.dump_data(json)

        return create_future(Payload(encoded_product))

    @router.fire_and_forget("set_completed")
    @with_product_repository
    async def set_completed_fire_and_forget(payload: Payload, composite_metadata: CompositeMetadata, repo: ProductRepository):
        data = api.load_data(payload.data)
        product_id = data["id"]

        await repo.set_completed(product_id, completed=True)

    @router.stream("get_all_uncompleted")
    async def get_all_uncompleted_stream(payload: Payload, composite_metadata: CompositeMetadata) -> Publisher:
        data = api.load_data(payload.data)
        count = data["count"]

        publisher = product_getting_stream(limit=count)

        return publisher

    @router.channel("bulk_add")
    async def bulk_add_channel(payload: Payload, composite_metadata: CompositeMetadata) -> tuple[Optional[Publisher], Optional[Subscriber]]:
        data = api.load_data(payload.data)
        count = data["count"]

        subscriber = ProductCreatingSubscriber(limit=count)
        channel = product_creating_stream(limit=count, local_subscriber=subscriber)

        return channel, subscriber

    def factory():
        return RoutingRequestHandler(router=router)

    return factory
