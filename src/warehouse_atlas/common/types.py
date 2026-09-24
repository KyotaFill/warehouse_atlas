from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from warehouse_atlas.common.constants import Condition

type EntityId = UUID
type Quantity = Decimal
type Money = Decimal


@dataclass(frozen=True, slots=True)
class BucketKey:
    """
    Value Object biểu diễn 4 chiều hạt nhân xác định một ngăn số dư tồn kho:
    (product_id, location_id, lot_id, condition)
    """

    product_id: UUID
    location_id: UUID
    lot_id: UUID
    condition: Condition

    def __repr__(self) -> str:
        return (
            f"BucketKey(p={str(self.product_id)[:8]}.., "
            f"loc={str(self.location_id)[:8]}.., "
            f"lot={str(self.lot_id)[:8]}.., "
            f"cond={self.condition.value})"
        )


@dataclass(frozen=True, slots=True)
class BucketDelta:
    """Biến động số dư được tính toán trước khi commit."""

    key: BucketKey
    delta_on_hand: Decimal = Decimal("0")
    delta_reserved: Decimal = Decimal("0")
