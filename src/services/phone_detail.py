from typing import Sequence, Callable

from fastapi import HTTPException, status


from src.models import PhoneDetail
from src.schemas import CreatePhoneDetailRequest

from src.config import UnitOfWork


class PhoneService:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
    ) -> None:
        self.uow_factory = uow_factory

    async def create_phone_detail(
        self,
        payload: list[CreatePhoneDetailRequest]
    ) -> list[PhoneDetail]:

        async with self.uow_factory() as uow:
            phone_details = await uow.phones.create_phone_detail(payload)
            if len(payload) != len(phone_details):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        return phone_details

    async def get_phone_detail(
        self,
        phone_numbers: list[str]
    ) -> Sequence[PhoneDetail]:
        async with self.uow_factory() as uow:
            phone_details = await uow.phones.get_phone_detail(phone_numbers)
            if len(phone_numbers) != len(phone_details):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return phone_details
