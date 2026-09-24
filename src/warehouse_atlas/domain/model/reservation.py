from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from warehouse_atlas.common.constants import ReservationStatus
from warehouse_atlas.common.exceptions import ValidationError
from warehouse_atlas.common.types import BucketKey


@dataclass
class StockReservation:
    """
    Cam kết giữ hàng cho một dòng đơn bán (SO Line).
    Ngăn chặn bán/xuất trùng lặp khi nhiều đơn cùng cần một lô hàng.
    """

    id: UUID
    so_line_id: UUID
    bucket_key: BucketKey
    reserved_qty: Decimal
    consumed_qty: Decimal = Decimal("0")
    released_qty: Decimal = Decimal("0")
    status: ReservationStatus = ReservationStatus.ACTIVE
    expires_at: datetime | None = None

    @property
    def remaining_qty(self) -> Decimal:
        return max(Decimal("0"), self.reserved_qty - self.consumed_qty - self.released_qty)

    def consume(self, qty: Decimal) -> None:
        if qty > self.remaining_qty:
            raise ValidationError(
                f"Lượng tiêu thụ ({qty}) vượt quá lượng giữ còn lại ({self.remaining_qty})"
            )
        self.consumed_qty += qty
        if self.remaining_qty == Decimal("0"):
            self.status = ReservationStatus.CONSUMED
        else:
            self.status = ReservationStatus.PARTIALLY_CONSUMED

    def release(self, qty: Decimal) -> None:
        if qty > self.remaining_qty:
            raise ValidationError(
                f"Lượng nhả ({qty}) vượt quá lượng giữ còn lại ({self.remaining_qty})"
            )
        self.released_qty += qty
        if self.remaining_qty == Decimal("0"):
            self.status = ReservationStatus.RELEASED


@dataclass(frozen=True, slots=True)
class ReservationEvent:
    """Nhật ký biến động lượng giữ hàng (ALLOCATE, CONSUME, RELEASE, EXPIRE)."""

    id: UUID
    reservation_id: UUID
    event_type: str  # ALLOCATE, CONSUME, RELEASE, EXPIRE
    quantity: Decimal
    created_at: datetime
    document_line_id: UUID | None = None
