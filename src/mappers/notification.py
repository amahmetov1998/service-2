from aiokafka import ConsumerRecord

from src.models import Notification


def message_to_orm(message: ConsumerRecord) -> Notification:
    return Notification(
        user_uuid=message.value['user_uuid'],
        notification_uuid=message.value['notification_uuid'],
        type=message.value['type'],
        title=message.value['title'],
        message=message.value['message'],
    )
