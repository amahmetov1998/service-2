import logging
from typing import Callable

from aiokafka import AIOKafkaConsumer, ConsumerRecord, AIOKafkaProducer
from aiokafka.errors import (
    KafkaConnectionError,
    KafkaTimeoutError,
    RequestTimedOutError,
)
from pydantic import ValidationError

from models.enums import OperationState
from src.schemas import NotificationCreateSchema, Message
from src.config import ApplicationUnitOfWork

log = logging.getLogger(__name__)


class Consumer:

    def __init__(
            self,
            dlq_producer: AIOKafkaProducer,
            kafka_consumer: AIOKafkaConsumer,
            uow_factory: Callable[[], ApplicationUnitOfWork],
            notification_topic_name: str,
            dead_letter_topic_name: str
    ):
        self.dlq_producer = dlq_producer
        self.kafka_consumer = kafka_consumer
        self.uow_factory = uow_factory
        self.dead_letter_topic_name = dead_letter_topic_name
        self.notification_topic_name = notification_topic_name

    async def run(self) -> None:
        try:
            async for message in self.kafka_consumer:
                await self._handle_message(message)
        except (KafkaConnectionError, KafkaTimeoutError, RequestTimedOutError) as e:
            log.exception(
                "Broker error while sending to dlq. error_type=%s, error=%s",
                type(e).__name__,
                e,
            )
            return

    async def _handle_message(self, message_br: ConsumerRecord):
        header = dict(message_br.headers)
        msg_id_bytes = header.get("Idempotency-Key")
        if msg_id_bytes:
            message_id = msg_id_bytes.decode()
        else:
            log.warning(
                "Message received without idempotency-key. topic=%s, partition=%s, offset=%s",
                message_br.topic,
                message_br.partition,
                message_br.offset,
            )
            await self._send_to_dlq(message_br=message_br)
            return
        try:
            NotificationCreateSchema.model_validate(message_br.value["payload"])
        except ValidationError as err:
            log.warning(
                "Invalid message schema. topic=%s, partition=%s, offset=%s, error=%s",
                message_br.topic,
                message_br.partition,
                message_br.offset,
                err.errors(),
            )
            await self._send_to_dlq(message_br=message_br)
            return

        state = OperationState.NEW
        async with self.uow_factory() as uow:
            await uow.messages.lock_message_id(message_id=message_id)
            message = await uow.messages.get_message(message_id=message_id)
            if message:
                message_dict = Message.model_validate(message).model_dump()
                if message_br.value["payload"] != message_dict:
                    log.warning(
                        "Idempotency conflict: message_id=%s already exists with different payload. "
                        "topic=%s, partition=%s, offset=%s",
                        message_id,
                        message_br.topic,
                        message_br.partition,
                        message_br.offset,
                    )
                    state = OperationState.CONFLICT
                elif message_br.value == message_dict:
                    state = OperationState.DUPLICATE
            else:
                await uow.notifications.create_notification(values=message_br.value["payload"])
                await uow.messages.create_message(
                    message_id=message_id, message=message_br.value["payload"]
                )

        if state == OperationState.CONFLICT:
            await self._send_to_dlq(message_br=message_br)

        elif state == OperationState.DUPLICATE or state == OperationState.NEW:
            await self.kafka_consumer.commit()

    async def _send_to_dlq(self, message_br: ConsumerRecord):
        try:
            await self.dlq_producer.send_and_wait(
                headers=list(message_br.headers),
                topic=self.dead_letter_topic_name,
                value=message_br.value,
            )
            await self.kafka_consumer.commit()
            # непонятно нужно ли коммитить тут и переходить к следующему сообщению?
        except (
            KafkaConnectionError,
            KafkaTimeoutError,
            RequestTimedOutError,
        ) as e:
            log.exception(
                "Broker error while sending to dlq. error_type=%s, error=%s",
                type(e).__name__,
                e,
            )
