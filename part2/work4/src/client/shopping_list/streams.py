import logging
from asyncio import Event
from typing import AsyncGenerator

from rsocket.payload import Payload
from reactivestreams.publisher import DefaultPublisher, Publisher
from reactivestreams.subscriber import Subscriber, Subscription
from reactivestreams.subscriber import DefaultSubscriber
from rsocket.streams.stream_from_async_generator import StreamFromAsyncGenerator

from tooling import api

LOG = logging.getLogger(__name__)


def data_creating_stream(
    count: int,
    wait_for_requester_complete: Event,
) -> Publisher:
    async def generator() -> AsyncGenerator[tuple[Payload, bool], None]:
        for current_response in range(count):
            is_complete = (current_response + 1) == count

            data = input("data in json string > ")
            encoded_data = api.dump_data(api.load_data(data)) 

            if is_complete:
                wait_for_requester_complete.set()

            yield Payload(encoded_data), is_complete

    return StreamFromAsyncGenerator(generator=generator)


class DataCreatingSubscriber(DefaultSubscriber):
    def __init__(self, count: int, wait_for_responder_complete: Event, *args, **kwargs):
        self.count = count
        self._wait_for_responder_complete = wait_for_responder_complete
        super().__init__(*args, **kwargs)

    def on_next(self, value: Payload, is_complete: bool = False):
        data = api.load_data(value.data)

        LOG.info(f"[RC] Created {data}")

        if is_complete:
            self._wait_for_responder_complete.set()

    def on_error(self, exception: Exception):
        self._wait_for_responder_complete.set()
        super().on_error(exception)

    def on_complete(self):
        self._wait_for_responder_complete.set()

    def on_subscribe(self, subscription: Subscription):
        self.subscription = subscription
        self.subscription.request(self.count)


class DataGettingSubscriber(DefaultSubscriber):
    def __init__(self, count: int, wait_for_responder_complete: Event, *args, **kwargs):
        self.count = count
        self._wait_for_responder_complete = wait_for_responder_complete
        super().__init__(*args, **kwargs)

    def on_next(self, value: Payload, is_complete: bool = False):
        data = api.load_data(value.data)

        LOG.info(f"[RS] Received: {data}")

        if is_complete:
            self._wait_for_responder_complete.set()

    def on_error(self, exception: Exception):
        self._wait_for_responder_complete.set()
        super().on_error(exception)

    def on_complete(self):
        self._wait_for_responder_complete.set()

    def on_subscribe(self, subscription: Subscription):
        self.subscription = subscription
        self.subscription.request(self.count)
