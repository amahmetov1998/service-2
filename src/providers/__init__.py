from .app_dependencies import create_app_dependencies
from .repository import create_phone_repository
from .unit_of_work import create_uow_factory

__all__ = [
    "create_app_dependencies",
    "create_uow_factory",
    "create_phone_repository",
]
