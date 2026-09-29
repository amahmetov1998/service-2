import logging
from contextlib import asynccontextmanager
from typing import Callable
from uuid import UUID

from aiokafka import ConsumerRecord
from pydantic import ValidationError

from src.exceptions import BrokerUnavailableError
from src.broker import ServiceBroker
from src.models import OperationState
from src.schemas import NotificationCreateSchema, MessageSchema
from src.mappers import notification as notification_mapper, message as message_mapper
from src.config import UnitOfWork, WorkerContext, RepositoryFactory

log = logging.getLogger(__name__)


class Worker:

    def __init__(
        self,
        broker: ServiceBroker,
        uow_factory: Callable[[], UnitOfWork],
        repository_factory: RepositoryFactory,
        notification_topic_name: str,
        dead_letter_topic_name: str
    ):
        self.broker = broker
        self._uow_factory = uow_factory
        self._repo_factory = repository_factory
        self.dead_letter_topic_name = dead_letter_topic_name
        self.notification_topic_name = notification_topic_name

    @asynccontextmanager
    async def _tx(self):
        async with self._uow_factory() as uow:
            yield WorkerContext(
                uow=uow,
                repo_factory=self._repo_factory,
            )

    async def run(self) -> None:
        async for message in self.broker.consume():
            await self._handle_message(message)

    async def _handle_message(self, message: ConsumerRecord) -> None:
        header = dict(message.headers)
        msg_id_bytes = header.get("Idempotency-Key")
        if msg_id_bytes:
            message_id_str = msg_id_bytes.decode()
        else:
            log.warning(
                "Message received without idempotency-key. topic=%s, partition=%s, offset=%s",
                message.topic,
                message.partition,
                message.offset,
            )
            await self._send_to_dlq(message=message)
            return
        try:
            message_id = UUID(message_id_str)
        except ValueError:
            log.warning(
                "Invalid idempotency-key. topic=%s, partition=%s, offset=%s",
                message.topic,
                message.partition,
                message.offset,
            )
            await self._send_to_dlq(message=message)
            return
        try:
            notification_msg = NotificationCreateSchema.model_validate(message.value).model_dump(mode="json")
        except ValidationError as err:
            log.warning(
                "Invalid message schema. topic=%s, partition=%s, offset=%s, error=%s",
                message.topic,
                message.partition,
                message.offset,
                err.errors(),
            )
            await self._send_to_dlq(message=message)
            return

        state = OperationState.NEW
        async with self._tx() as tx:
            await tx.messages.lock_message_id(message_id=message_id)
            message_db = await tx.messages.get_message(message_id=message_id)
            if message_db:
                message_dict = MessageSchema.model_validate(message_db.message).model_dump(mode="json")
                if notification_msg != message_dict:
                    log.warning(
                        "Idempotency conflict: message_id=%s already exists with different payload."
                        "topic=%s, partition=%s, offset=%s",
                        message_id,
                        message.topic,
                        message.partition,
                        message.offset,
                    )
                    state = OperationState.CONFLICT
                elif notification_msg == message_dict:
                    state = OperationState.DUPLICATE
            else:
                notification = notification_mapper.message_to_orm(message=message)
                await tx.notifications.create_notification(notification=notification)
                message_orm = message_mapper.message_to_orm(message_id=message_id, message=message)
                await tx.messages.create_message(message=message_orm)

        if state == OperationState.CONFLICT:
            await self._send_to_dlq(message=message)

        elif state == OperationState.DUPLICATE:
            await self.broker.commit(message=message)
        elif state == OperationState.NEW:
            await self.broker.commit(message=message)

    async def _send_to_dlq(self, message: ConsumerRecord):
        try:
            await self.broker.send_to_dlq(message=message, topic_name=self.dead_letter_topic_name)
        except BrokerUnavailableError as e:
            log.warning(
                "Broker unavailable while sending message to dlq."
                "topic=%s, partition=%s, offset=%s, error=%s",
                self.dead_letter_topic_name,
                message.partition,
                message.offset,
                e,
            )
            raise
