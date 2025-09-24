# cqrsex/Application/Interfaces/Repositories/IOutboxRepository.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from cqrsex.Domain.models.OutboxEvent import OutboxEvent


class IOutboxRepository(ABC):
    @abstractmethod
    def using(self, db_alias: str) -> "IOutboxRepository":
        """Return a clone of this repository that targets the given Django DB alias (e.g. 'default', 'auth', 'market')."""
        ...

    @abstractmethod
    def add(
        self,
        aggregate_type: str,
        aggregate_id: Any,
        event_type: str,
        payload: Dict[str, Any],
        tenant_id: str = "main",
        headers: Optional[Dict[str, Any]] = None,
    ) -> OutboxEvent:
        """Persist a new outbox event in the current DB alias and return it."""
        ...
