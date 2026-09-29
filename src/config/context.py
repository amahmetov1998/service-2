from .unit_of_work import UnitOfWork, RepositoryFactory


class WorkerContext:
    def __init__(self, uow: UnitOfWork, repo_factory: RepositoryFactory):
        self.uow = uow
        self.notifications = repo_factory.notification(uow.session)
        self.messages = repo_factory.message(uow.session)
