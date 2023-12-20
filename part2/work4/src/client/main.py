import asyncio
import logging

from rsocket.helpers import single_transport_provider
from rsocket.rsocket_client import RSocketClient
from rsocket.transports.tcp import TransportTCP
from rsocket.extensions.mimetypes import WellKnownMimeTypes

from config import config
from shopping_list.handlers import handle_input


async def main():
    logging.info(f"Connecting to server at {config.SERVER_HOST}:{config.SERVER_PORT}")

    connection = await asyncio.open_connection(
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
    )

    async with RSocketClient(
        single_transport_provider(TransportTCP(*connection)),
        metadata_encoding=WellKnownMimeTypes.MESSAGE_RSOCKET_COMPOSITE_METADATA,
        fragment_size_bytes=1_000_000,
    ) as client:
        await handle_input(client=client)


def setup():
    logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    setup()

    asyncio.run(main())