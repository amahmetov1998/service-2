from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import PhoneDetail
from src.schemas import PhoneDetailResponse, CreatePhoneDetailRequest

from src.service import phone_detail as phones_service
from src.utils import db_helper

router = APIRouter()


@router.post("/phones", response_model=list[PhoneDetailResponse])
async def create_phone_details(
    phone_details: list[CreatePhoneDetailRequest],
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
) -> list[PhoneDetail]:
    return await phones_service.create_phone_detail(session, phone_details)


@router.get("/phones", response_model=list[PhoneDetailResponse])
async def get_phone_details(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    phone_numbers: list[str] = Query(...),
) -> Sequence[PhoneDetail]:
    return await phones_service.get_phone_detail(session, phone_numbers)
