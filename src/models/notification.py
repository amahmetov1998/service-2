from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base
from .enums import NotificationType


class Notification(Base):
    """Модель уведомления"""

    user_uuid: Mapped[UUID]
    type: Mapped[NotificationType]
    title: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(String(200))
