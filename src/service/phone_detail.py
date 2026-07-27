from typing import Sequence

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc

from src.models import PhoneDetail
from src.schemas import CreatePhoneDetailRequest

from src.repository import phone_detail as phone_repository


async def create_phone_detail(
    session: AsyncSession, payload: list[CreatePhoneDetailRequest]
) -> list[PhoneDetail]:

    phone_details = await phone_repository.create_phone_detail(session, payload)
    try:
        await session.commit()
    except exc.IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return phone_details


async def get_phone_detail(
    session: AsyncSession, phone_numbers: list[str]
) -> Sequence[PhoneDetail]:
    phone_details = await phone_repository.get_phone_detail(session, phone_numbers)
    if len(phone_numbers) != len(phone_details):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return phone_details
