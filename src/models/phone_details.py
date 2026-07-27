from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from src.enums import OperatorType, RegionType
from .base import Base


class PhoneDetail(Base):
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    operator_type: Mapped[OperatorType] = mapped_column(nullable=False)
    region_type: Mapped[RegionType] = mapped_column(nullable=False)
    is_spam: Mapped[bool] = mapped_column(default=False, nullable=False)
