from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Operation(Base):
    operation_id: Mapped[UUID] = mapped_column(unique=True)
    response: Mapped[list[dict]] = mapped_column(JSONB)
