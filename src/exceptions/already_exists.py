from src.schemas import AlreadyExistsDetails


class AlreadyExistsError(Exception):
    def __init__(self, message: str, error_code: str, details: AlreadyExistsDetails):
        super().__init__(message)
        self.details = details
        self.error_code = error_code
