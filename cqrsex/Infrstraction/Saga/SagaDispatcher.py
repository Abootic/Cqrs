# cqrsex/Infrstraction/Saga/SagaDispatcher.py
from __future__ import annotations
import logging
from types import SimpleNamespace
from typing import Any, Optional, Callable

from injector import inject
from django.db import transaction, connections, DEFAULT_DB_ALIAS

from cqrsex.Application.Interfaces.Common.ISagaDispatcher import ISagaDispatcher
from cqrsex.Application.Interfaces.Common.ISaga import ISaga

log = logging.getLogger(__name__)

def _infer_alias(using: Optional[str]) -> str:
    if using:
        return using
    try:
        for alias in connections:
            if connections[alias].in_atomic_block:
                return alias
    except Exception:
        pass
    return DEFAULT_DB_ALIAS

class SagaDispatcher(ISagaDispatcher):
    @inject
    def __init__(self, saga: ISaga) -> None:
        self._saga = saga

    def _dispatch_now(self, evt: Any) -> None:
        log.info(
            "[SagaDispatcher] dispatching entity=%s action=%s db=%s",
            getattr(evt, "entity", None),
            getattr(evt, "action", None),
            getattr(evt, "db_alias", None),
        )
        try:
            self._saga.process(evt)
        except Exception:
            log.exception("Saga dispatch failed")

    def after_commit(
        self,
        evt_or_factory: Any | Callable[[], Any],
        *,
        using: Optional[str] = None,
    ) -> None:
        alias = _infer_alias(using)
        log.info("[SagaDispatcher] scheduled on_commit for alias=%s", alias)

        def _runner():
            evt = evt_or_factory() if callable(evt_or_factory) else evt_or_factory
            self._dispatch_now(evt)

        transaction.on_commit(_runner, using=alias)

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
        alias = _infer_alias(using)
        evt = SimpleNamespace(
            entity=entity,
            action=action,
            event_type=event_type,
            payload=payload or {},
            aggregate_id=aggregate_id,
            db_alias=alias,
            command=command,
        )
        self.after_commit(evt, using=alias)
