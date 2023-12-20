import asyncio
import logging
from asyncio import Event

from rsocket.payload import Payload
from rsocket.rsocket_client import RSocketClient
from rsocket.extensions.helpers import route, composite

from tooling import api
from .streams import DataCreatingSubscriber, DataGettingSubscriber
from .streams import data_creating_stream

LOG = logging.getLogger(__name__)


async def handle_input(client: RSocketClient):
    try:
        while True:
            command = input("command > ")

            if command == "get":
                await request_get(client=client)
            elif command == "complete":
                await request_set_completed(client=client)
            elif command == "get-uncompleted":
                await request_get_uncompleted(client=client)
            elif command == "add":
                await request_bulk_add(client=client)
    except asyncio.CancelledError:
        LOG.debug("CANCEL")
        pass


async def request_get(client: RSocketClient):
    id_ = input("id > ")

    data = {"id": id_}
    encoded_data = api.dump_data(data)

    composite_metadata = composite(route("get"))
    result = await client.request_response(Payload(encoded_data, composite_metadata))

    LOG.info(f"[RR] Received data: {api.load_data(result.data)}")


async def request_set_completed(client: RSocketClient):
    id_ = input("id > ")

    data = {"id": id_}
    encoded_data = api.dump_data(data)

    composite_metadata = composite(route("set_completed"))
    await client.fire_and_forget(Payload(encoded_data, composite_metadata))


async def request_get_uncompleted(client: RSocketClient):
    internal_completion_event = Event()

    count = int(input("count > "))
    data = {"count": count}
    encoded_data = api.dump_data(data)

    composite_metadata = composite(route("get_all_uncompleted"))
    publisher = client.request_stream(Payload(encoded_data, composite_metadata))

    subscriber = DataGettingSubscriber(
        count=count,
        wait_for_responder_complete=internal_completion_event,
    )
    publisher.initial_request_n(count).subscribe(subscriber)

    await internal_completion_event.wait()


async def request_bulk_add(client: RSocketClient):
    internal_completion_event = Event()
    external_completion_event = Event()

    count = int(input("count > "))
    data = {"count": count}
    encoded_data = api.dump_data(data)

    publisher = data_creating_stream(
        count=count,
        wait_for_requester_complete=external_completion_event,
    )

    composite_metadata = composite(route("bulk_add"))
    response_publisher = client.request_channel(
        payload=Payload(encoded_data, composite_metadata),
        publisher=publisher,
    )

    susbcriber = DataCreatingSubscriber(
        count=count,
        wait_for_responder_complete=internal_completion_event,
    )
    response_publisher.initial_request_n(100).subscribe(susbcriber)

    await external_completion_event.wait()
    await internal_completion_event.wait()
