from .service import get_phone_service
from .uow import get_uow_factory, get_repository_factory

__all__ = [
    "get_phone_service",
    "get_uow_factory",
    "get_repository_factory",
]
