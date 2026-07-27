from uuid import UUID

from pydantic import BaseModel

from src.enums import OperatorType, RegionType
from src.schemas.base import BaseResponse


class CreatePhoneDetailRequest(BaseModel):
    phone_number: str
    operator_type: OperatorType
    region_type: RegionType
    is_spam: bool = False


class PhoneDetailResponse(CreatePhoneDetailRequest, BaseResponse):
    uuid: UUID
