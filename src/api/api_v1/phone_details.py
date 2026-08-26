from typing import Annotated, Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query

from src.dependencies import get_phone_service

from src.models import PhoneDetail
from src.schemas import PhoneDetailResponse, CreatePhoneDetailRequest
from src.services import PhoneService

router = APIRouter(prefix="/phones", tags=["phones"])


@router.post("")
async def create_phone_details(
    phone_details: list[CreatePhoneDetailRequest],
    phone_service: Annotated[PhoneService, Depends(get_phone_service)],
    operation_id: UUID = Header(..., alias="Idempotency-Key"),
) -> list[PhoneDetailResponse]:
    return await phone_service.create_phone_detail(
        payload=phone_details, operation_id=operation_id
    )


@router.get("", response_model=list[PhoneDetailResponse])
async def get_phone_details(
    phone_service: Annotated[PhoneService, Depends(get_phone_service)],
    phone_numbers: list[str] = Query(...),
) -> Sequence[PhoneDetail]:
    return await phone_service.get_phone_detail(phone_numbers=phone_numbers)
