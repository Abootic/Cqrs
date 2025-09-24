# cqrsex/Application/Interfaces/Common/ISaga.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class ISaga(ABC):
    @abstractmethod
    def process(self, event: Any) -> None:
        ...
