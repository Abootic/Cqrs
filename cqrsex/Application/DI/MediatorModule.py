# cqrsex/Application/DI/MediatorModule.py
from __future__ import annotations
import logging
from typing import Any, Callable, Dict, Type
from injector import Module, provider, singleton, Injector

from cqrsex.Application.Mediator.mediator import Mediator
from cqrsex.Application.Mediator.behaviors import TransactionBehavior
from cqrsex.Application.Interfaces.Common.IUnitOfWork import IUnitOfWork
from cqrsex.Application.Mediator.registry import build_handler_factories
from cqrsex.Application.Mediator.import_handlers import import_under

log = logging.getLogger(__name__)

class MediatorModule(Module):
    @singleton
    @provider
    def provide_mediator(self, injector: Injector) -> Mediator:
        import_under(["cqrsex.Application.CQRS"])

        handlers: Dict[Type[Any], Callable[[], Any]] = build_handler_factories(injector)
        if not handlers:
            raise RuntimeError("No handlers registered. Check @handler_for on classes, and __init__.py files.")

        log.info("Mediator registered %d handlers: %s",
                 len(handlers), ", ".join(t.__name__ for t in handlers.keys()))

        uow_factory: Callable[[], IUnitOfWork] = lambda: injector.get(IUnitOfWork)
        return Mediator(handlers=handlers, behaviors=[TransactionBehavior(uow_factory)], cache_handlers=True)
