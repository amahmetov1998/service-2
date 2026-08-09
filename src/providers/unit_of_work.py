from typing import Callable

from src.config import AppDependencies
from src.config.unit_of_work import UnitOfWork


def create_uow_factory(
    deps: AppDependencies,
) -> Callable[[], UnitOfWork]:
    return lambda: UnitOfWork(session_factory=deps.session_factory)
