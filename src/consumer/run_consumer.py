import asyncio
import json
import logging
import signal

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from src.config import (
    create_session_factory,
    settings,
    create_engine,
    configure_logging,
)
from src.dependencies import get_uow
from src.consumer.consumer import Consumer

log = logging.getLogger(__name__)


async def run_consumer():
    configure_logging(settings.logging)
    engine = create_engine(settings.db.url)
    session_factory = create_session_factory(engine)
    uow_factory = get_uow(session_factory)
    dlq_producer = AIOKafkaProducer(
        bootstrap_servers=settings.broker.url,
        acks=settings.broker.acks,
        enable_idempotence=settings.broker.enable_idempotence,
        value_serializer=lambda x: json.dumps(x).encode(),
        max_batch_size=settings.broker.max_batch_size,
        linger_ms=settings.broker.linger_ms,
    )
    kafka_consumer = AIOKafkaConsumer(
        settings.broker.notification_topic_name,
        bootstrap_servers=settings.broker.url,
        group_id=settings.broker.group_id,
        auto_offset_reset=settings.broker.auto_offset_reset,
        enable_auto_commit=settings.broker.enable_auto_commit,
        max_poll_records=settings.broker.max_poll_records,
        value_deserializer=lambda value: json.loads(value.decode()),
    )
    consumer = Consumer(
        dlq_producer=dlq_producer,
        kafka_consumer=kafka_consumer,
        uow_factory=uow_factory,
        dead_letter_topic_name=settings.broker.dead_letter_topic_name,
        notification_topic_name=settings.broker.notification_topic_name,
    )

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    try:
        while not stop_event.is_set():
            try:
                await dlq_producer.start()
                await kafka_consumer.start()
                await consumer.run()
            except Exception as e:
                log.exception(
                    "Unexpected error in producer. Error type=%s, error=%s",
                    type(e).__name__,
                    e,
                )
            try:
                await asyncio.wait_for(
                    stop_event.wait(),
                    timeout=settings.broker.poll_interval,
                )
            except asyncio.TimeoutError:
                pass

    finally:
        await kafka_consumer.stop()
        await dlq_producer.stop()


if __name__ == "__main__":
    asyncio.run(run_consumer())
