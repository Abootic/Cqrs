# cqrsex/Application/Sagas/OutboxSaga.py
from __future__ import annotations
from typing import Any
from injector import inject
from cqrsex.Application.Interfaces.Repositories.IOutboxRepository import IOutboxRepository
from cqrsex.Application.Interfaces.Common.ISaga import ISaga

class OutboxSaga(ISaga):
    @inject
    def __init__(self, outbox_repo: IOutboxRepository) -> None:
        self._outbox_repo = outbox_repo

    def process(self, event: Any) -> None:
        db = getattr(event, "db_alias", "default")
        entity = getattr(event, "entity", None) or "Unknown"
        action = getattr(event, "action", None) or "Unknown"
        agg_id = getattr(event, "aggregate_id", None)
        payload = getattr(event, "payload", {}) or {}

        self._outbox_repo.using(db).add(
            aggregate_type=entity,
            aggregate_id=agg_id,
            event_type=action,
            payload=payload,
            tenant_id=payload.get("tenant_id", "main"),
        )
