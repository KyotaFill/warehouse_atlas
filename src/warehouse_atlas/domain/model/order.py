from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

from warehouse_atlas.common.constants import OrderStatus


@dataclass
class PurchaseOrderLine:
    id: UUID
    order_id: UUID
    product_id: UUID
    uom_id: UUID
    ordered_qty: Decimal
    received_qty: Decimal = Decimal("0")
    unit_price: Decimal = Decimal("0")

    @property
    def remaining_qty(self) -> Decimal:
        return max(Decimal("0"), self.ordered_qty - self.received_qty)


@dataclass
class PurchaseOrder:
    id: UUID
    code: str
    supplier_id: UUID
    warehouse_id: UUID
    status: OrderStatus
    order_date: date
    expected_delivery_date: date | None = None
    lines: list[PurchaseOrderLine] = field(default_factory=list)


@dataclass
class SalesOrderLine:
    id: UUID
    order_id: UUID
    product_id: UUID
    uom_id: UUID
    ordered_qty: Decimal
    reserved_qty: Decimal = Decimal("0")
    shipped_qty: Decimal = Decimal("0")
    unit_price: Decimal = Decimal("0")

    @property
    def unreserved_qty(self) -> Decimal:
        return max(Decimal("0"), self.ordered_qty - self.reserved_qty - self.shipped_qty)

    @property
    def remaining_to_ship(self) -> Decimal:
        return max(Decimal("0"), self.ordered_qty - self.shipped_qty)


@dataclass
class SalesOrder:
    id: UUID
    code: str
    customer_id: UUID
    warehouse_id: UUID
    status: OrderStatus
    order_date: date
    delivery_date: date | None = None
    lines: list[SalesOrderLine] = field(default_factory=list)
