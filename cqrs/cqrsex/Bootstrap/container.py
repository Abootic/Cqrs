from injector import Injector
from cqrsex.Application.DI.MediatorModule import MediatorModule
from cqrsex.Infrstraction.DI.RepositoryModule import RepositoryModule
from cqrsex.Infrstraction.DI.UoWModule import UoWModule
from cqrsex.Application.Mediator.mediator import Mediator

_injector: Injector | None = None

def get_injector() -> Injector:
    global _injector
    if _injector is None:
        _injector = Injector([RepositoryModule(), UoWModule(), MediatorModule()])
    return _injector

def get_mediator() -> Mediator:
    return get_injector().get(Mediator)
