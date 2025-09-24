from dataclasses import dataclass
from typing import Optional
from cqrsex.Application.Mediator.contracts import IQuery
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(frozen=True)
class ListUsers(IQuery[ConcreteResultT]):
    page: int = 1
    page_size: int = 20
    q: Optional[str] = None          # search username/email
    user_type: Optional[str] = None  # filter by role
