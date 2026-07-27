from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from src.models import PhoneDetail
from src.schemas import CreatePhoneDetailRequest


async def create_phone_detail(
    session: AsyncSession, payload: list[CreatePhoneDetailRequest]
) -> list[PhoneDetail]:
    phone_details = [PhoneDetail(**item.model_dump()) for item in payload]
    session.add_all(phone_details)
    return phone_details


async def get_phone_detail(
    session: AsyncSession, phone_numbers: list[str]
) -> Sequence[PhoneDetail]:
    stmt = select(PhoneDetail).where(PhoneDetail.phone_number.in_(phone_numbers))
    result: Result = await session.execute(stmt)
    phone_details = result.scalars().all()
    return phone_details
