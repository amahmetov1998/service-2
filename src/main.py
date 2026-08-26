import asyncio

import uvicorn
from fastapi import FastAPI

from src.application import create_app
from src.api import healthcheck_router, phones_router
from src.config import settings


def get_app() -> FastAPI:
    app: FastAPI = create_app()
    app.include_router(healthcheck_router)
    app.include_router(phones_router)
    return app


async def main() -> None:
    uvicorn.run(
        "main:get_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
        factory=settings.run.factory,
    )


if __name__ == "__main__":
    asyncio.run(main())
