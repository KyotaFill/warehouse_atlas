from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class Lot:
    """
    Lô hàng nội bộ (Internal Lot).
    Mỗi lần nhận hàng sinh ra một internal lot để lưu vết giá nhập, ngày nhận và hạn sử dụng.
    """
    id: UUID
    product_id: UUID
    internal_lot_code: str
    manufacturer_lot_code: str | None
    expires_on: date | None
    manufactured_on: date | None
    unit_cost: Decimal
    received_at: datetime
    is_blocked: bool = False
    block_reason: str | None = None

    def block(self, reason: str) -> None:
        self.is_blocked = True
        self.block_reason = reason

    def unblock(self) -> None:
        self.is_blocked = False
        self.block_reason = None
