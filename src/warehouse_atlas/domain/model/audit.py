from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AuditEvent:
    id: UUID
    entity_name: str
    entity_id: UUID
    action: str
    actor_id: UUID
    occurred_at: datetime
    payload_before: dict[str, Any] | None = None
    payload_after: dict[str, Any] | None = None
