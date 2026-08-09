from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.config import AppDependencies


def create_app(
    deps: AppDependencies,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        _app.state.deps = deps

        yield

        await deps.engine.dispose()

    app = FastAPI(
        lifespan=lifespan,
        default_response_class=JSONResponse,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
