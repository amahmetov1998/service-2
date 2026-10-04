from uuid import UUID

from sqlalchemy import select, func, Result, insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Operation


class OperationRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def lock_operation_id(self, operation_id: UUID) -> None:
        key = str(operation_id)
        await self.session.execute(
            select(
                func.pg_advisory_xact_lock(
                    func.hashtextextended(key, 0),
                ),
            )
        )

    async def get_operation(self, operation_id: UUID) -> Operation | None:
        stmt = select(Operation).where(Operation.operation_id == operation_id)
        result: Result = await self.session.execute(stmt)
        operation: Operation | None = result.scalar_one_or_none()
        return operation

    async def create_operation(self, operation_id: UUID, response: list[dict]) -> None:
        stmt = (
            insert(Operation)
            .values(operation_id=operation_id, response=response)
        )
        await self.session.execute(stmt)
