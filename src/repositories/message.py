from uuid import UUID

from sqlalchemy import select, func, Result
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Message


class MessageRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def lock_message_id(self, message_id: UUID) -> None:
        key = str(message_id)
        await self.session.execute(
            select(
                func.pg_advisory_xact_lock(
                    func.hashtextextended(key, 0),
                ),
            )
        )

    async def get_message(self, message_id: UUID) -> Message | None:
        stmt = select(Message).where(Message.message_id == message_id)
        result: Result = await self.session.execute(stmt)
        message: Message | None = result.scalar_one_or_none()
        return message

    async def create_message(self, message: Message) -> Message:
        self.session.add(message)
        return message
