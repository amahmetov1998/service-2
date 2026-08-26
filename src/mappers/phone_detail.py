from src.schemas import PhoneDetailResponse
from src.models import PhoneDetail


def orm_to_dict(phone_details: list[PhoneDetail]) -> list[dict]:
    return [
        PhoneDetailResponse.model_validate(item).model_dump(mode="json") for item in phone_details
    ]


def dict_to_schema(phone_details: list[dict]) -> list[PhoneDetailResponse]:
    return [PhoneDetailResponse.model_validate(item) for item in phone_details]


def orm_to_schema(phone_details: list[PhoneDetail]) -> list[PhoneDetailResponse]:
    return [PhoneDetailResponse.model_validate(item) for item in phone_details]
