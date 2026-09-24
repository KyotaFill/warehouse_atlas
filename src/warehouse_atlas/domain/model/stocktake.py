from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from warehouse_atlas.common.constants import StocktakeStatus
from warehouse_atlas.common.types import BucketKey


@dataclass
class StocktakeLine:
    id: UUID
    stocktake_id: UUID
    bucket_key: BucketKey
    snapshot_qty: Decimal  # Số hệ thống ghi nhận lúc chụp (không hiển thị cho người đếm mù)
    counted_qty: Decimal | None = None  # None = chưa đếm, 0 = đã đếm và thấy hết hàng
    difference_qty: Decimal | None = None  # counted_qty - snapshot_qty


@dataclass
class Stocktake:
    """
    Phiên kiểm kê mù tại một vị trí/kho.
    Khi COUNTING, location bị freeze để ngăn biến động trong lúc đếm.
    """

    id: UUID
    warehouse_id: UUID
    location_id: UUID
    code: str
    status: StocktakeStatus
    created_by: UUID
    created_at: datetime
    closed_at: datetime | None = None
    adjustment_document_id: UUID | None = None
    lines: list[StocktakeLine] = field(default_factory=list)
