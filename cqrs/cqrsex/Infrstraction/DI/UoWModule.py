from typing import Callable
from injector import Module, provider, singleton
from cqrsex.Application.Interfaces.Common.IUnitOfWork import IUnitOfWork
from cqrsex.Infrstraction.UoW.UnitOfWork import UnitOfWork

class UoWModule(Module):
    @singleton
    @provider
    def provide_uow_factory(self) -> Callable[[], IUnitOfWork]:
        return lambda: UnitOfWork()
