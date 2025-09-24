from dataclasses import dataclass
from typing import Optional
from cqrsex.Application.Mediator.contracts import ICommand
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(frozen=True)
class UpdateUser(ICommand[ConcreteResultT]):
    id: int
    # fields a user can update on themselves
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None

    # admin-only fields
    user_type: Optional[str] = None
    is_active: Optional[bool] = None

    # context from controller
    acting_user_id: Optional[int] = None
    acting_is_admin: bool = False
