from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional, Callable

class ISagaDispatcher(ABC):
    @abstractmethod
    def after_commit(
        self,
        evt_or_factory: Any | Callable[[], Any],
        *,
        using: Optional[str] = None,
    ) -> None:
        """Schedule an event to be dispatched AFTER the active transaction commits."""

    @abstractmethod
    def emit(
        self,
        *,
        entity: Optional[str] = None,
        action: Optional[str] = None,
        event_type: Optional[str] = None,
        payload: Optional[dict] = None,
        aggregate_id: Any = None,
        command: Optional[str] = None,
        using: Optional[str] = None,
    ) -> None:
        """Build a routing-friendly event and schedule it post-commit."""
