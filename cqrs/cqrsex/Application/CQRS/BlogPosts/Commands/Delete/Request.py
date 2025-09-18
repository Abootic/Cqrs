from dataclasses import dataclass
from cqrsex.Application.Mediator.contracts import ICommand
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(frozen=True)
class DeleteBlogPost(ICommand[ConcreteResultT]):
    id: int
