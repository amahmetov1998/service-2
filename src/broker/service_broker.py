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
            except (KafkaConnectionError, KafkaTimeoutError, RequestTimedOutError):
                raise BrokerUnavailableError("Broker unavailable")
        return coroutine_wrapper

    @functools.wraps(request_func)
    async def async_generator_wrapper(*args, **kwargs):
        try:
            async for item in request_func(*args, **kwargs):
                yield item
        except (KafkaConnectionError, KafkaTimeoutError, RequestTimedOutError):
            raise BrokerUnavailableError("Broker unavailable")
    return async_generator_wrapper


class ServiceBroker:
    def __init__(self, producer: AIOKafkaProducer, consumer: AIOKafkaConsumer):
        self.producer = producer
        self.consumer = consumer

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

    async def commit(self, message: ConsumerRecord):
        await self.consumer.commit(
            {
                TopicPartition(message.topic, message.partition): message.offset + 1
            }
        )
