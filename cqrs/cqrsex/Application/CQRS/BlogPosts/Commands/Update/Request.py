from dataclasses import dataclass
from typing import Optional
from cqrsex.Application.Mediator.contracts import ICommand
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(frozen=True)
class UpdateBlogPost(ICommand[ConcreteResultT]):
    id: int
    title: Optional[str] = None
    body: Optional[str] = None
