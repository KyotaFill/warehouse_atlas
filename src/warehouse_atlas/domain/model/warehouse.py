from dataclasses import dataclass
from uuid import UUID

from warehouse_atlas.common.constants import LocationType


@dataclass(frozen=True, slots=True)
class Warehouse:
    id: UUID
    code: str
    name: str
    is_active: bool = True


@dataclass(frozen=True, slots=True)
class Location:
    """
    Vị trí vật lý trong kho (Zone, Aisle, Rack, Shelf, Bin).
    Tổ chức theo cây phân cấp (parent_id) nhưng cùng thuộc một kho (warehouse_id).
    """

    id: UUID
    warehouse_id: UUID
    code: str
    type: LocationType
    parent_id: UUID | None = None
    is_active: bool = True
    is_frozen: bool = False  # Bị đóng băng khi đang kiểm kê
