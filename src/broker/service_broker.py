import functools
import inspect
from typing import Sequence

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer, ConsumerRecord, TopicPartition
from aiokafka.errors import (
    KafkaConnectionError,
    KafkaTimeoutError,
    RequestTimedOutError,
)

from src.exceptions import BrokerUnavailableError


def handle_transport_errors(request_func):
    if inspect.iscoroutinefunction(request_func):
        @functools.wraps(request_func)
        async def coroutine_wrapper(*args, **kwargs):
            try:
                return await request_func(*args, **kwargs)
            except (KafkaConnectionError, KafkaTimeoutError, RequestTimedOutError) as e:
                raise BrokerUnavailableError("Broker unavailable") from e

        return coroutine_wrapper

    @functools.wraps(request_func)
    async def async_generator_wrapper(*args, **kwargs):
        try:
            async for item in request_func(*args, **kwargs):
                yield item
        except (KafkaConnectionError, KafkaTimeoutError, RequestTimedOutError) as e:
            raise BrokerUnavailableError("Broker unavailable") from e

    return async_generator_wrapper


class ServiceBroker:
    def __init__(self, producer: AIOKafkaProducer, consumer: AIOKafkaConsumer, group_id: str) -> None:
        self.producer = producer
        self.consumer = consumer
        self.group_id = group_id

    @handle_transport_errors
    async def send_and_wait_ack(
            self, headers: Sequence[tuple[str, bytes]], topic_name: str, value
    ) -> None:
        await self.producer.send_and_wait(
            headers=headers,
            topic=topic_name,
            value=value,
        )

    @handle_transport_errors
    async def consume(self):
        async for message in self.consumer:
            yield message

    @handle_transport_errors
    async def commit(self, message: ConsumerRecord):
        await self.consumer.commit(
            {
                TopicPartition(message.topic, message.partition): message.offset + 1
            }
        )

    @handle_transport_errors
    async def send_to_dlq(self, message: ConsumerRecord, topic_name: str) -> None:
        await self.producer.begin_transaction()

        try:
            await self.producer.send_and_wait(
                headers=list(message.headers),
                topic=topic_name,
                value=message.value,
            )
            await self.producer.send_offsets_to_transaction(
                offsets={
                    TopicPartition(
                        message.topic,
                        message.partition,
                    ): message.offset + 1,
                },
                group_id=self.group_id
            )
            await self.producer.commit_transaction()

        except Exception:
            await self.producer.abort_transaction()
            raise
