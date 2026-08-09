from typing import Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from src.models import PhoneDetail
from src.schemas import CreatePhoneDetailRequest


class PhoneRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create_phone_detail(
        self,
        payload: list[CreatePhoneDetailRequest]
    ) -> list[PhoneDetail]:
        phones_payload = [item.model_dump() for item in payload]
        result = await self.session.execute(
            insert(PhoneDetail)
            .on_conflict_do_nothing(index_elements=[PhoneDetail.phone_number])
            .returning(PhoneDetail),
            phones_payload,
        )
        return list(result.scalars().all())

    async def get_phone_detail(
        self,
        phone_numbers: list[str]
    ) -> Sequence[PhoneDetail]:
        stmt = select(PhoneDetail).where(PhoneDetail.phone_number.in_(phone_numbers))
        result: Result = await self.session.execute(stmt)
        return result.scalars().all()
