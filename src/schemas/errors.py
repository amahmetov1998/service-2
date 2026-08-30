from typing import Any

from pydantic import BaseModel


class AlreadyExistsDetails(BaseModel):
    detail: list[str]


class NotFoundDetails(BaseModel):
    detail: list[str]


class IdempotencyConflictDetails(BaseModel):
    detail: str


class ErrorResponse(BaseModel):
    message: str
    error_code: str | None
    details: Any | None = None
