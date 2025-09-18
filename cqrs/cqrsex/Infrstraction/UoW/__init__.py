import logging
from django.db import transaction

from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Interfaces.Common.IUnitOfWork import IUnitOfWork


log = logging.getLogger(__name__)

class DjangoUnitOfWork(IUnitOfWork):
    def __init__(self, repo_manager: IRepositoryManager):
        self._repo = repo_manager
        self._ctx = None
        self._committed = False

    @property
    def repo(self) -> IRepositoryManager:
        return self._repo

    def __enter__(self):
        self._ctx = transaction.atomic()
        self._ctx.__enter__()
        self._committed = False
        return self

    def commit(self) -> None:
        self._committed = True

    def rollback(self) -> None:
        transaction.set_rollback(True)

    def __exit__(self, exc_type, exc, tb):
        if exc_type or not self._committed:
            transaction.set_rollback(True)
        else:
            transaction.on_commit(lambda: log.info("UoW committed"))
        return self._ctx.__exit__(exc_type, exc, tb)
