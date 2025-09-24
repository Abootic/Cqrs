# cqrsex/Application/DI/SagaDispatchModule.py
from injector import Module, provider, singleton
from cqrsex.Application.Interfaces.Common.ISaga import ISaga
from cqrsex.Application.Interfaces.Common.ISagaDispatcher import ISagaDispatcher

class SagaDispatchModule(Module):
    @singleton
    @provider
    def provide_saga_dispatcher(self, saga: ISaga) -> ISagaDispatcher:
        # lazy import to avoid import cycles at startup
        from cqrsex.Infrstraction.Saga.SagaDispatcher import SagaDispatcher
        return SagaDispatcher(saga)
