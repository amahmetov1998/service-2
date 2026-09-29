from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from src.models import PhoneDetail


class PhoneRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create_phone_detail(
        self,
        payload: list[dict[str, Any]],
    ) -> list[PhoneDetail]:
        result = await self.session.execute(
            insert(PhoneDetail)
            .on_conflict_do_nothing(index_elements=[PhoneDetail.phone_number])
            .returning(PhoneDetail),
            payload,
        )
        return list(result.scalars().all())

    async def get_phone_detail(
        self,
        phone_numbers: list[str]
    ) -> list[PhoneDetail]:
        stmt = select(PhoneDetail).where(PhoneDetail.phone_number.in_(phone_numbers))
        result: Result = await self.session.execute(stmt)
        return list(result.scalars().all())
