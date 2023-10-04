import asyncio
import logging

import reactivex
from rsocket.helpers import single_transport_provider
from rsocket.payload import Payload
from rsocket.rsocket_client import RSocketClient
from rsocket.transports.tcp import TransportTCP

from config import config
from tooling import api
from streams import DataCreatingPublisher
from streams import DataCreatingSubscriber


async def handle_input(client: RSocketClient):
    try:
        while True:
            command = input("command > ")

            if command == "get":
                id_ = input("id > ")

                data = {"id": id_}
                encoded_data = api.dump_data(data)
                result = await client.request_response(Payload(encoded_data))
                print("Received data:", api.load_data(result.data))

            elif command == "complete":
                id_ = input("id > ")

                data = {"id": id_}
                encoded_data = api.dump_data(data)
                await client.fire_and_forget(Payload(encoded_data))

            elif command == "get-uncompleted":
                count = int(input("count > "))
                data = {"count": count}
                encoded_data = api.dump_data(data)

                publisher = client.request_stream(Payload(encoded_data))
                publisher.subscribe(DataCreatingSubscriber(count))

            elif command == "add":
                count = int(input("count > "))
                data = {"count": count}
                encoded_data = api.dump_data(data)

                publisher = reactivex.create(DataCreatingPublisher(count))

                response_publisher = client.request_channel(
                    payload=Payload(encoded_data),
                    publisher=publisher,
                )
                response_publisher.subscribe(DataCreatingSubscriber(count))


    except asyncio.CancelledError:
        pass


async def main():
    logging.info(f"Connecting to server at {config.SERVER_HOST}:{config.SERVER_PORT}")

    connection = await asyncio.open_connection(
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
    )

    async with RSocketClient(
        single_transport_provider(TransportTCP(*connection)),
    ) as client:
        task = asyncio.create_task(handle_input(client))
        await asyncio.sleep(5)

        task.cancel()
        await task


def setup():
    logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    setup()

    asyncio.run(main())