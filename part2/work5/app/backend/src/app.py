from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .filemanager.router import router as filemanager_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Simple decentralized distributed file app",
        description="App for file managment as example of decentralized distributed app",
        version="1.0",
        debug=True,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(filemanager_router, prefix="/files")

    @app.get("/health")
    async def health() -> str:
        return "OK"

    return app
