# cqrsex/Infrstraction/Repositories/OutboxRepository.py
from __future__ import annotations
from django.db import transaction
from cqrsex.Domain.models.OutboxEvent import OutboxEvent
from cqrsex.Application.Interfaces.Repositories.IOutboxRepository import IOutboxRepository

class OutboxRepository(IOutboxRepository):
    def __init__(self, db_alias: str = "default"):
        self.db_alias = db_alias

    def using(self, db_alias: str) -> "OutboxRepository":
        return OutboxRepository(db_alias=db_alias)

    def add(
        self,
        aggregate_type: str,
        aggregate_id,
        event_type: str,
        payload: dict,
        tenant_id: str = "main",
    ) -> OutboxEvent:
        with transaction.atomic(using=self.db_alias):
            return OutboxEvent.objects.using(self.db_alias).create(
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                event_type=event_type,
                payload=payload,
                tenant_id=tenant_id,
            )
