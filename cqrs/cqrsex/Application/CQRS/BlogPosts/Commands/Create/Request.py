from dataclasses import dataclass
from cqrsex.Application.Mediator.contracts import ICommand
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(frozen=True)
class CreateBlogPost(ICommand[ConcreteResultT]):
    title: str
    body: str
    author_id: int
