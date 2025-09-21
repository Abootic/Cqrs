# cqrsex/Infrstraction/DI/UoWModule.py
from injector import Module, Binder
from cqrsex.Application.Interfaces.Common.IUnitOfWork import IUnitOfWork
from cqrsex.Infrstraction.UoW.UnitOfWork import UnitOfWork

class UoWModule(Module):
    def configure(self, binder: Binder) -> None:
        # New UnitOfWork each time it's requested (default NoScope). Do NOT @singleton a UoW.
        binder.bind(IUnitOfWork, to=UnitOfWork)
