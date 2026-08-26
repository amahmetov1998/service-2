from typing import Self

from src.repositories import PhoneRepository, OperationRepository


class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is None:
                await self.session.commit()
            else:
                await self.session.rollback()
        finally:
            await self.session.close()


class ApplicationUnitOfWork(UnitOfWork):
    async def __aenter__(self) -> Self:
        await super().__aenter__()
        self.operations = OperationRepository(self.session)
        self.phones = PhoneRepository(self.session)
        return self
