# cqrsex/Application/CQRS/BlogPosts/Queries/List/Request.py
from typing import Optional, Annotated
from pydantic.dataclasses import dataclass
from pydantic import Field, PositiveInt
from cqrsex.Application.Mediator.contracts import IQuery
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(config={'extra': 'forbid'}, frozen=True, slots=True)
class ListBlogPosts(IQuery[ConcreteResultT]):
    page:      Annotated[int, Field(ge=1)] = 1
    page_size: Annotated[int, Field(ge=1, le=200)] = 20
    author_id: Optional[PositiveInt] = None
