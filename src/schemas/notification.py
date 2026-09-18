from uuid import UUID

from pydantic import BaseModel, Field

from src.models import NotificationType


class NotificationCreateSchema(BaseModel):
    notification_uuid: UUID
    user_uuid: UUID
    type: NotificationType
    title: str = Field(max_length=20)
    message: str = Field(max_length=200)
