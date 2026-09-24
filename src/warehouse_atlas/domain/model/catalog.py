from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Category:
    id: UUID
    code: str
    name: str
    parent_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class Uom:
    id: UUID
    code: str
    name: str


@dataclass(frozen=True, slots=True)
class ProductUom:
    id: UUID
    product_id: UUID
    uom_id: UUID
    conversion_factor: Decimal  # Hệ số quy đổi ra đơn vị cơ sở (base UOM)


@dataclass(frozen=True, slots=True)
class ProductBarcode:
    id: UUID
    product_id: UUID
    barcode: str
    uom_id: UUID


@dataclass
class Product:
    """
    Danh mục sản phẩm (SKU).
    Lưu ý kiến trúc: Product là danh mục thông tin, KHÔNG chứa thuộc tính quantity hay stock.
    Số lượng thực tế nằm ở StockBalance theo 4 chiều: (product_id, location_id, lot_id, condition).
    """
    id: UUID
    sku: str
    name: str
    category_id: UUID
    base_uom_id: UUID
    is_perishable: bool = False
    shelf_life_days: int | None = None
    min_shelf_life_days: int = 0
    is_active: bool = True
    barcodes: list[ProductBarcode] = field(default_factory=list)
    uoms: list[ProductUom] = field(default_factory=list)
