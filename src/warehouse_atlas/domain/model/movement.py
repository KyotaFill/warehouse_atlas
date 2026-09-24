from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from warehouse_atlas.common.constants import Condition


@dataclass(frozen=True, slots=True)
class StockMovement:
    """
    Sổ kho (Append-Only Ledger) - Nguồn gốc sự thật về số lượng tồn kho.
    Mỗi dòng chứng từ POSTED sinh đúng một bản ghi StockMovement.
    Không bao giờ UPDATE hoặc DELETE StockMovement.
    """
    id: UUID
    document_line_id: UUID
    product_id: UUID
    lot_id: UUID
    quantity: Decimal  # Luôn dương
    recorded_at: datetime
    from_location_id: UUID | None
    to_location_id: UUID | None
    from_condition: Condition | None
    to_condition: Condition | None
