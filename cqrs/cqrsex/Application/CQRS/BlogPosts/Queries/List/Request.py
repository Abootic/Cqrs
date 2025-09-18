from dataclasses import dataclass
from typing import Optional
from cqrsex.Application.Mediator.contracts import IQuery
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(frozen=True)
class ListBlogPosts(IQuery[ConcreteResultT]):
    page: int = 1
    page_size: int = 20
    author_id: Optional[int] = None
