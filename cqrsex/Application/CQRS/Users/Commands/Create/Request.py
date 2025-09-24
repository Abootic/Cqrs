# cqrsex/Application/CQRS/Users/Commands/Create/Request.py
from dataclasses import dataclass
from cqrsex.Application.Mediator.contracts import ICommand
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(frozen=True)
class CreateUser(ICommand[ConcreteResultT]):
    username: str
    password: str
    email: str
    user_type: str = "CUSTOMER"
    allow_anonymous: bool = False  # <-- keep this
    db_alias: str | None = None

