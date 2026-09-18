from typing import Any
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Message(Base):
    message_id: Mapped[UUID] = mapped_column(unique=True)
    message: Mapped[dict[str, Any]] = mapped_column(JSONB)
