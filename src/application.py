from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.config import (
    create_engine,
    create_session_factory,
    settings,
)


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        _app.state.engine = create_engine(settings.db.url)
        _app.state.session_factory = create_session_factory(
            engine=app.state.engine,
        )

        yield

        await _app.state.engine.dispose()

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
