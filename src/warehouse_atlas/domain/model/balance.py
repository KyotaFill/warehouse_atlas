from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from warehouse_atlas.common.exceptions import InsufficientStockError
from warehouse_atlas.common.types import BucketKey


@dataclass
class StockBalance:
    """
    Số dư tồn kho tại một Bucket (4 chiều).
    Sổ movement là nguồn gốc, StockBalance là snapshot/projection giao dịch để đọc và khóa nhanh.
    """
    id: UUID
    bucket_key: BucketKey
    on_hand: Decimal
    reserved: Decimal
    version: int = 1

    def __post_init__(self) -> None:
        if self.on_hand < Decimal("0"):
            raise InsufficientStockError(f"on_hand không được âm: {self.on_hand}")
        if self.reserved < Decimal("0"):
            raise InsufficientStockError(f"reserved không được âm: {self.reserved}")
        if self.reserved > self.on_hand:
            raise InsufficientStockError(
                f"reserved ({self.reserved}) không được vượt quá on_hand ({self.on_hand})"
            )

    @property
    def free_qty(self) -> Decimal:
        """Lượng vật lý chưa bị giữ (chưa kiểm tra điều kiện xuất/hạn dùng)."""
        return self.on_hand - self.reserved

    def can_reserve(self, requested_qty: Decimal) -> bool:
        return self.free_qty >= requested_qty

    def apply_reservation(self, qty: Decimal) -> None:
        if not self.can_reserve(qty):
            raise InsufficientStockError(
                f"Không đủ lượng khả dụng để giữ hàng: yêu cầu {qty}, còn {self.free_qty}"
            )
        self.reserved += qty

    def release_reservation(self, qty: Decimal) -> None:
        if qty > self.reserved:
            raise InsufficientStockError(
                f"Lượng giải phóng ({qty}) vượt quá reserved ({self.reserved})"
            )
        self.reserved -= qty

    def consume_reservation(self, qty: Decimal) -> None:
        if qty > self.reserved or qty > self.on_hand:
            raise InsufficientStockError(
                f"Không thể tiêu thụ {qty}: on_hand={self.on_hand}, reserved={self.reserved}"
            )
        self.reserved -= qty
        self.on_hand -= qty
