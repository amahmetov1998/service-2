from typing import Annotated, Callable

from fastapi import Depends

from src.config import UnitOfWork
from src.services import PhoneService
from .unit_of_work import get_uow


def get_phone_service(
    uow_factory: Annotated[Callable[[], UnitOfWork], Depends(get_uow)],
) -> PhoneService:
    return PhoneService(
        uow_factory=uow_factory,
    )
