from uuid import UUID

from aiokafka import ConsumerRecord

from src.models import Message


def message_to_orm(message_id: UUID, message: ConsumerRecord) -> Message:
    return Message(message_id=message_id, message=message.value)
