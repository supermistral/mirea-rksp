import logging

from rsocket.payload import Payload
from reactivestreams.subscriber import Subscription
from reactivestreams.subscriber import DefaultSubscriber

from tooling import api

LOG = logging.getLogger(__name__)


class DataCreatingPublisher:
    def __init__(self, count: int):
        self.count = count

    def __call__(self, observer, scheduler):
        for _ in range(self.count):
            data = input("data in json string > ")
            encoded_data = api.dump_data(api.load_data(data))

            observer.on_next(Payload(encoded_data))

        observer.on_complete()


class DataCreatingSubscriber(DefaultSubscriber):
    def __init__(self, count: int, *args, **kwargs):
        self.count = count
        super().__init__(*args, **kwargs)

    def on_next(self, value, is_complete=False):
        data = api.load_data(value.data)

        LOG.info(f"[RC] Created {data}")
 
    def on_subscribe(self, subscription: Subscription):
        self.subscription = subscription
        self.subscription.request(self.count + 1)
