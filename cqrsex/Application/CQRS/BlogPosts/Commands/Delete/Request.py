# cqrsex/Application/CQRS/BlogPosts/Commands/Delete/Request.py
from pydantic.dataclasses import dataclass
from pydantic import PositiveInt
from cqrsex.Application.Mediator.contracts import ICommand
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(config={'extra': 'forbid'}, frozen=True, slots=True)
class DeleteBlogPost(ICommand[ConcreteResultT]):
    id: PositiveInt
