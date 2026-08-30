from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from src.exceptions import (
    NotFoundError,
    AlreadyExistsError,
)
from src.schemas import ErrorResponse


def _error_response(
    status_code: int,
    message: str,
    details: Any | None = None,
    error_code: str | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(message=message, details=details, error_code=error_code).model_dump(),
    )


def register_errors_handlers(app):
    @app.exception_handler(NotFoundError)
    def not_found_handler(request: Request, exc: NotFoundError):

        return _error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=str(exc),
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        return _error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Request validation failed",
            details=exc.errors(),
        )

    @app.exception_handler(AlreadyExistsError)
    def already_exists_handler(request: Request, exc: AlreadyExistsError):

        return _error_response(
            status_code=status.HTTP_409_CONFLICT,
            message=str(exc),
            details=exc.details,
            error_code=exc.error_code,
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ):

        return _error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(exc),
        )
