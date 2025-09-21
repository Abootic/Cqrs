# cqrsex/Application/CQRS/BlogPosts/Queries/Get/Request.py
from pydantic.dataclasses import dataclass
from pydantic import PositiveInt
from cqrsex.Application.Mediator.contracts import IQuery
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(config={'extra': 'forbid'}, frozen=True, slots=True)
class GetBlogPost(IQuery[ConcreteResultT]):
    id: PositiveInt
