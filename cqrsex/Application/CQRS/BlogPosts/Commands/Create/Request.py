# cqrsex/Application/CQRS/BlogPosts/Commands/Create/Request.py
from typing import Annotated
from pydantic.dataclasses import dataclass
from pydantic import Field, PositiveInt
from cqrsex.Application.Mediator.contracts import ICommand
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass(config={'extra': 'forbid', 'str_strip_whitespace': True}, frozen=True, slots=True)
class CreateBlogPost(ICommand[ConcreteResultT]):
    title: Annotated[str, Field(min_length=1, max_length=256, strip_whitespace=True)]
    author_id: PositiveInt                                # <-- move this up (required, no default)
    body:  Annotated[str, Field(strip_whitespace=True, max_length=50_000)] = ""  # default last
