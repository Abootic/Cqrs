# cqrsex/Application/DI/SagaModule.py
from injector import Module, provider, singleton
from cqrsex.Application.Mediator.mediator import Mediator
from cqrsex.Application.Interfaces.Common.ISaga import ISaga
from cqrsex.Application.Interfaces.Repositories.IOutboxRepository import IOutboxRepository

class SagaModule(Module):
    @singleton
    @provider
    def provide_saga(self, mediator: Mediator, outbox_repo: IOutboxRepository) -> ISaga:
        # lazy imports to avoid cycles
        from cqrsex.Infrstraction.Saga.MultiSaga import MultiSaga
        from cqrsex.Application.Sagas.OutboxSaga import OutboxSaga
        from cqrsex.Application.Sagas.GenericCrudSaga import GenericCrudSaga
        return MultiSaga([
            OutboxSaga(outbox_repo),   # accepts IOutboxRepository fine
            GenericCrudSaga(mediator),
        ])
