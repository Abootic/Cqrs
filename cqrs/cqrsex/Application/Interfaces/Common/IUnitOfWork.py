# cqrsex/Application/Interfaces/Common/IUnitOfWork.py
from abc import ABC, abstractmethod
from typing import Optional

class IUnitOfWork(ABC):
    """Transaction boundary for commands. No repo properties here."""

    @abstractmethod
    def __enter__(self) -> "IUnitOfWork": ...
    @abstractmethod
    def __exit__(self, exc_type, exc, tb) -> Optional[bool]: ...
    @abstractmethod
    def commit(self) -> None: ...
    @abstractmethod
    def rollback(self) -> None: ...
