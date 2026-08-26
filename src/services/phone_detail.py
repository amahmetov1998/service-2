from typing import Sequence, Callable
from uuid import UUID
from fastapi import HTTPException, status

from src.mappers import phone_detail as phone_detail_mapper
from src.models import PhoneDetail
from src.schemas import CreatePhoneDetailRequest, PhoneDetailResponse

from src.config import ApplicationUnitOfWork


class PhoneService:
    def __init__(
        self,
        uow_factory: Callable[[], ApplicationUnitOfWork],
    ) -> None:
        self.uow_factory = uow_factory

    async def create_phone_detail(
        self,
        payload: list[CreatePhoneDetailRequest],
        operation_id: UUID
    ) -> list[PhoneDetailResponse]:
        async with self.uow_factory() as uow:
            await uow.operations.lock_operation_id(operation_id=str(operation_id))
            operation = await uow.operations.get_operation(operation_id=operation_id)

            if not operation:
                details = await uow.phones.create_phone_detail(payload)

                if len(payload) != len(details):
                    incoming = [item.phone_number for item in payload]
                    inserted = [item.phone_number for item in details]
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=list(set(incoming) - set(inserted)),
                    )
                response = phone_detail_mapper.orm_to_dict(phone_details=details)
                await uow.operations.create_operation(operation_id=operation_id, response=response)
                phone_details = phone_detail_mapper.orm_to_schema(
                    phone_details=details
                )
            else:
                phone_details = phone_detail_mapper.dict_to_schema(phone_details=operation.response)
            return phone_details

    async def get_phone_detail(
        self,
        phone_numbers: list[str]
    ) -> Sequence[PhoneDetail]:
        async with self.uow_factory() as uow:
            extracted = await uow.phones.get_phone_detail(phone_numbers)
            if len(phone_numbers) != len(extracted):
                inserted = [item.phone_number for item in extracted]
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=list(set(phone_numbers) - set(inserted)),
                )
        return extracted
