from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import (
    PhoneRepository,
    OperationRepository,
    MessageRepository,
    NotificationRepository
)


class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self._transaction = await self.session.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self._transaction.__aexit__(
                exc_type,
                exc_val,
                exc_tb,
            )
        finally:
            await self.session.close()


class RepositoryFactory:
    def message(self, session: AsyncSession) -> MessageRepository:
        return MessageRepository(session)

    def notification(self, session: AsyncSession) -> NotificationRepository:
        return NotificationRepository(session)

    def phone_detail(self, session: AsyncSession) -> PhoneRepository:
        return PhoneRepository(session)

    def operation(self, session: AsyncSession) -> OperationRepository:
        return OperationRepository(session)
