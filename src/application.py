from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.api import router as api_router

from contextlib import asynccontextmanager

from src.utils.db_helper import db_helper


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # startup
    yield
    # shutdown
    await db_helper.dispose()


def get_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=JSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app
