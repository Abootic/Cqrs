# cqrsex/Application/CQRS/BlogPosts/Commands/Update/Request.py
from typing import Optional, Annotated
from pydantic.dataclasses import dataclass
from pydantic import Field, PositiveInt
from cqrsex.Application.Mediator.contracts import ICommand
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(config={'extra': 'forbid', 'str_strip_whitespace': True}, frozen=True, slots=True)
class UpdateBlogPost(ICommand[ConcreteResultT]):
    id: PositiveInt
    title: Optional[Annotated[str, Field(min_length=1, max_length=256, strip_whitespace=True)]] = None
    body:  Optional[Annotated[str, Field(strip_whitespace=True, max_length=50_000)]] = None
    # Handler enforces: at least one of {title, body} must be provided.
