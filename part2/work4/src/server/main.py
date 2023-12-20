import asyncio
import logging

from rsocket.rsocket_server import RSocketServer
from rsocket.transports.tcp import TransportTCP

from server.shopping_list.handler import handler_factory
from server.config import config
from server.db import init_models


async def run_server():
    logging.info(f"Starting server at {config.HOST}:{config.PORT}")

    def session(*connection):
        RSocketServer(
            TransportTCP(*connection),
            handler_factory=handler_factory(),
        )

    server = await asyncio.start_server(
        session,
        host=config.HOST,
        port=config.PORT,
    )

    async with server:
        await server.serve_forever()


async def setup():
    logging.basicConfig(level=logging.INFO)
    await init_models()


async def main():
    await setup()
    await run_server()


if __name__ == "__main__":
    asyncio.run(main())
