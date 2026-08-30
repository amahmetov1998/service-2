from typing import Sequence, Callable
from uuid import UUID

from src.exceptions import AlreadyExistsError, NotFoundError, IdempotencyConflictError
from src.mappers import phone_detail as phone_detail_mapper
from src.models import PhoneDetail, ErrorCode
from src.schemas import (
    CreatePhoneDetailRequest,
    PhoneDetailResponse,
    AlreadyExistsDetails,
    NotFoundDetails,
    IdempotencyConflictDetails
)

from src.config import ApplicationUnitOfWork
from src.utils import normalize_payload


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
            await uow.operations.lock_operation_id(operation_id=operation_id)
            operation = await uow.operations.get_operation(operation_id=operation_id)

            if operation:
                payload_to_dict = phone_detail_mapper.schema_to_dict(payload=payload)
                operation_payload = phone_detail_mapper.response_to_payload(operation.response)

                if normalize_payload(payload_to_dict) != normalize_payload(operation_payload):
                    raise IdempotencyConflictError(
                        message="Operation id already exists with different payload",
                        error_code=ErrorCode.IDEMPOTENCY_KEY_REUSED,
                        details=IdempotencyConflictDetails(
                            detail=f"Operation_id {operation_id} already used with different payload"
                        )
                    )
                return phone_detail_mapper.dict_to_schema(response=operation.response)
            details = await uow.phones.create_phone_detail(payload)

            if len(payload) != len(details):
                inserted_numbers = {detail.phone_number for detail in details}
                incoming_numbers = {item.phone_number for item in payload}

                conflicting_numbers = list(incoming_numbers - inserted_numbers)
                raise AlreadyExistsError(
                    message=f"Phones {conflicting_numbers} already exist",
                    error_code=ErrorCode.PHONE_ALREADY_EXISTS,
                    details=AlreadyExistsDetails(detail=conflicting_numbers)
                )
            response = phone_detail_mapper.orm_to_dict(phone_details=details)
            await uow.operations.create_operation(operation_id=operation_id, response=response)
            return phone_detail_mapper.orm_to_schema(
                phone_details=details
            )

    async def get_phone_detail(
        self,
        phone_numbers: list[str]
    ) -> Sequence[PhoneDetail]:
        async with self.uow_factory() as uow:
            extracted = await uow.phones.get_phone_detail(phone_numbers)
            if len(phone_numbers) != len(extracted):
                inserted = [item.phone_number for item in extracted]
                phones_not_found = list(set(phone_numbers) - set(inserted))
                raise NotFoundError(
                    message=f"Phones {phones_not_found} not found",
                    details=NotFoundDetails(detail=phones_not_found)
                )
        return extracted
