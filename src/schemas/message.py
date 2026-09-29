from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MessageSchema(BaseModel):
    type: str
    title: str
    message: str
    user_uuid: UUID
    notification_uuid: UUID

    model_config = ConfigDict(from_attributes=True)
