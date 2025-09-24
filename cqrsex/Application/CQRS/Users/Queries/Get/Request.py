from dataclasses import dataclass
from cqrsex.Application.Mediator.contracts import IQuery
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(frozen=True)
class GetUser(IQuery[ConcreteResultT]):
    id: int
