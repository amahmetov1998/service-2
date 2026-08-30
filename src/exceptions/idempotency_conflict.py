from src.schemas import IdempotencyConflictDetails


class IdempotencyConflictError(Exception):
    def __init__(self, message: str, error_code: str, details: IdempotencyConflictDetails):
        super().__init__(message)
        self.details = details
        self.error_code = error_code
