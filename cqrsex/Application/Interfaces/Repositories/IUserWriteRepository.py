from abc import ABC, abstractmethod
from typing import Any

from cqrsex.Domain.models.User import User

class IUserWriteRepository(ABC):
    @abstractmethod
    def add(self, user:User) -> Any: ...
    @abstractmethod
    def update(self, user:User) -> Any: ...
    @abstractmethod
    def delete_permanently(self, user:User) -> None: ...
