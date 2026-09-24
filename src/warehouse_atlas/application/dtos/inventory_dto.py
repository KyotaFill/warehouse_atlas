from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from warehouse_atlas.common.constants import Condition


@dataclass(frozen=True, slots=True)
class DocumentLineInputDTO:
    line_number: int
    product_id: UUID
    uom_id: UUID
    quantity: Decimal
    quantity_base: Decimal
    lot_id: UUID
    from_location_id: UUID | None = None
    to_location_id: UUID | None = None
    from_condition: Condition | None = None
    to_condition: Condition | None = None
    po_line_id: UUID | None = None
    so_line_id: UUID | None = None
    reference_line_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class PostDocumentCommand:
    """Hợp đồng gửi lệnh ghi sổ chứng từ (Idempotent Posting Command)."""

    document_id: UUID
    expected_version: int
    idempotency_key: UUID
    actor_id: UUID
    canonical_payload_hash: str = "CANONICAL_HASH_PLACEHOLDER"
    lines: tuple[DocumentLineInputDTO, ...] = ()


@dataclass(frozen=True, slots=True)
class StockItemDTO:
    product_id: UUID
    sku: str
    product_name: str
    category_name: str
    location_code: str
    internal_lot_code: str
    condition: str
    on_hand: Decimal
    reserved: Decimal
    free_qty: Decimal
    uom_code: str
    expires_on: str | None
