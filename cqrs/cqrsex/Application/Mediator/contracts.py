from abc import ABC, abstractmethod
from typing import TypeVar, Generic

TResult = TypeVar("TResult")

class ICommand(ABC, Generic[TResult]): ...
class IQuery(ABC, Generic[TResult]): ...

C = TypeVar("C", bound=ICommand)
Q = TypeVar("Q", bound=IQuery)

class ICommandHandler(ABC, Generic[C, TResult]):
    @abstractmethod
    def handle(self, command: C) -> TResult: ...

class IQueryHandler(ABC, Generic[Q, TResult]):
    @abstractmethod
    def handle(self, query: Q) -> TResult: ...
