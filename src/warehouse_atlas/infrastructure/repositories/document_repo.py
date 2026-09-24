from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from warehouse_atlas.common.constants import DocumentStatus
from warehouse_atlas.infrastructure.orm.inventory_models import (
    InventoryDocument as InventoryDocumentRow,
)


class SqlAlchemyDocumentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def load_document(self, document_id: UUID) -> InventoryDocumentRow | None:
        stmt = select(InventoryDocumentRow).where(InventoryDocumentRow.id == document_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def mark_posted(
        self,
        document_id: UUID,
        posted_by: UUID,
        posted_at: datetime,
        idempotency_key: UUID,
        payload_hash: str,
    ) -> None:
        stmt = select(InventoryDocumentRow).where(InventoryDocumentRow.id == document_id)
        doc = self.session.execute(stmt).scalar_one()
        doc.status = DocumentStatus.POSTED.value
        doc.posted_by = posted_by
        doc.posted_at = posted_at
        doc.idempotency_key = idempotency_key
        doc.posting_payload_hash = payload_hash
        doc.version += 1
        self.session.flush()
