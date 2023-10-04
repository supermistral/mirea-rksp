import asyncio
import logging

from rsocket.rsocket_server import RSocketServer
from rsocket.transports.tcp import TransportTCP

from shopping_list.handler import Handler
from config import config
from db import init_models


async def run_server():
    logging.info(f"Starting server at {config.HOST}:{config.PORT}")

    def session(*connection):
        RSocketServer(TransportTCP(*connection), handler_factory=Handler)

    server = await asyncio.start_server(
        session,
        host=config.HOST,
        port=config.PORT,
    )

    async with server:
        await server.serve_forever()


async def setup():
    logging.basicConfig(level=logging.DEBUG)
    await init_models()


async def main():
    await setup()
    await run_server()


if __name__ == "__main__":
    setup()

    asyncio.run(main())
