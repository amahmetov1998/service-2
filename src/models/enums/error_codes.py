from enum import StrEnum


class ErrorCode(StrEnum):
    IDEMPOTENCY_KEY_REUSED = "idempotency_key_reused"
    PHONE_ALREADY_EXISTS = "phone_already_exists"


class OperationState(StrEnum):
    NEW = "new"
    DUPLICATE = "duplicate"
    CONFLICT = "conflict"
