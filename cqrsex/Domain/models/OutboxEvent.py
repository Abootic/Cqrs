import uuid
from django.db import models

class OutboxEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    aggregate_type = models.CharField(max_length=50)
    aggregate_id = models.UUIDField(default=uuid.uuid4)
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    tenant_id = models.CharField(max_length=20, default="main")
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    class Meta:
        db_table = "outbox_events"
        managed = True
