from src.schemas import PhoneDetailResponse, CreatePhoneDetailRequest
from src.models import PhoneDetail


def orm_to_dict(phone_details: list[PhoneDetail]) -> list[dict]:
    return [
        PhoneDetailResponse.model_validate(item).model_dump(mode="json") for item in phone_details
    ]


def dict_to_schema(response: list[dict]) -> list[PhoneDetailResponse]:
    return [PhoneDetailResponse.model_validate(item) for item in response]


def orm_to_schema(phone_details: list[PhoneDetail]) -> list[PhoneDetailResponse]:
    return [PhoneDetailResponse.model_validate(item) for item in phone_details]


def schema_to_dict(payload: list[CreatePhoneDetailRequest]) -> list[dict]:
    return [item.model_dump(mode="json") for item in payload]


def response_to_payload(response: list[dict]) -> list[dict]:
    return [
        CreatePhoneDetailRequest.model_validate(item).model_dump(mode="json")
        for item in response
    ]
