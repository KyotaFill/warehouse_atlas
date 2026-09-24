from typing import Any

from sqlalchemy.orm import Session

from warehouse_atlas.infrastructure.orm.audit_models import AuditEvent as AuditEventRow


class SqlAlchemyAuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def append(self, event: Any) -> None:
        row = AuditEventRow(
            id=event.id,
            entity_name=event.entity_name,
            entity_id=event.entity_id,
            action=event.action,
            actor_id=event.actor_id,
            recorded_at=event.recorded_at,
            payload_before=event.payload_before,
            payload_after=event.payload_after,
        )
        self.session.add(row)
        self.session.flush()
