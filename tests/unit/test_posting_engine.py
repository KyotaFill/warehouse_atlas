import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Self

from warehouse_atlas.application.dtos.inventory_dto import PostDocumentCommand
from warehouse_atlas.application.services.posting_engine import PostingEngine
from warehouse_atlas.common.constants import Condition, DocumentKind, DocumentStatus
from warehouse_atlas.common.types import BucketDelta, BucketKey
from warehouse_atlas.domain.model.document import InventoryDocument, InventoryDocumentLine


class InMemoryInventoryRepo:
    def __init__(self):
        self.locked_keys = []
        self.applied_deltas = []
        self.movements = []

    def lock_buckets(self, keys: list[BucketKey]) -> None:
        self.locked_keys.extend(keys)

    def apply_deltas(self, deltas: list[BucketDelta]) -> None:
        self.applied_deltas.extend(deltas)

    def append_movement(self, movement: Any) -> None:
        self.movements.append(movement)


class InMemoryDocumentRepo:
    def __init__(self):
        self.posted_records = []

    def mark_posted(
        self,
        document_id: uuid.UUID,
        posted_by: uuid.UUID,
        posted_at: datetime,
        idempotency_key: uuid.UUID,
        payload_hash: str,
    ) -> None:
        self.posted_records.append(
            (document_id, posted_by, posted_at, idempotency_key, payload_hash)
        )


class MockUoW:
    def __init__(self):
        self.inventory = InMemoryInventoryRepo()
        self.documents = InMemoryDocumentRepo()
        self.committed = False

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


def test_posting_engine_receipt():
    uow = MockUoW()
    doc_id = uuid.uuid4()
    p_id = uuid.uuid4()
    loc_id = uuid.uuid4()
    lot_id = uuid.uuid4()
    uom_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    idem_key = uuid.uuid4()

    line = InventoryDocumentLine(
        id=uuid.uuid4(),
        document_id=doc_id,
        line_number=1,
        product_id=p_id,
        uom_id=uom_id,
        quantity=Decimal("10"),
        quantity_base=Decimal("10"),
        lot_id=lot_id,
        from_location_id=None,
        to_location_id=loc_id,
        from_condition=None,
        to_condition=Condition.GOOD,
    )

    doc = InventoryDocument(
        id=doc_id,
        warehouse_id=uuid.uuid4(),
        code="REC-001",
        kind=DocumentKind.RECEIPT,
        status=DocumentStatus.APPROVED,
        created_by=actor_id,
        created_at=datetime.now(UTC),
        version=1,
        lines=[line],
    )

    cmd = PostDocumentCommand(
        document_id=doc_id,
        expected_version=1,
        idempotency_key=idem_key,
        actor_id=actor_id,
        canonical_payload_hash="test-hash",
        lines=(),
    )

    PostingEngine.post_in_uow(uow, doc, cmd)

    assert doc.status == DocumentStatus.POSTED
    assert len(uow.inventory.movements) == 1
    assert len(uow.inventory.applied_deltas) == 1
    assert uow.inventory.applied_deltas[0].delta_on_hand == Decimal("10")
