from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import PhoneService
from .session import get_session
from .uow import get_repository_factory


def get_phone_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PhoneService:
    repo_factory = get_repository_factory()
    phones = repo_factory.phone_detail(session)
    operations = repo_factory.operation(session)
    return PhoneService(
        phones=phones,
        operations=operations
    )
