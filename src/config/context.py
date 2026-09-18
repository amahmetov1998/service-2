from .unit_of_work import UnitOfWork, RepositoryFactory


class PhoneDetailContext:
    def __init__(self, uow: UnitOfWork, repo_factory: RepositoryFactory):
        self.uow = uow
        self.phones = repo_factory.phone_detail(uow.session)
        self.operations = repo_factory.operation(uow.session)


class WorkerContext:
    def __init__(self, uow: UnitOfWork, repo_factory: RepositoryFactory):
        self.uow = uow
        self.operations = repo_factory.operation(uow.session)
        self.notifications = repo_factory.notification(uow.session)
        self.messages = repo_factory.message(uow.session)
