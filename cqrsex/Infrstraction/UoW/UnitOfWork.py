# cqrsex/Infrstraction/UoW/UnitOfWork.py
from typing import Optional
from django.db import transaction
from cqrsex.Application.Interfaces.Common.IUnitOfWork import IUnitOfWork

class UnitOfWork(IUnitOfWork):
    def __init__(self) -> None:
        self._tx = None
        self._committed = False

    def __enter__(self) -> "UnitOfWork":
        self._tx = transaction.atomic()
        self._tx.__enter__()
        self._committed = False
        return self

    def commit(self) -> None:
        self._committed = True

    def rollback(self) -> None:
        transaction.set_rollback(True)

    def __exit__(self, exc_type, exc, tb) -> Optional[bool]:
        if exc_type or not self._committed:
            transaction.set_rollback(True)
        return self._tx.__exit__(exc_type, exc, tb)
