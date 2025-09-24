from dataclasses import dataclass
from cqrsex.Application.Mediator.contracts import ICommand
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(frozen=True)
class DeleteUser(ICommand[ConcreteResultT]):
    id: int
    acting_user_id: int | None = None
    acting_is_admin: bool = False
