from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import PhoneRepository


def create_phone_repository(
    session: AsyncSession,
) -> PhoneRepository:
    return PhoneRepository(session=session)
