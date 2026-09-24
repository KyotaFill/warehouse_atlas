from datetime import datetime
from decimal import Decimal
from typing import Any, Protocol
from uuid import UUID

from warehouse_atlas.common.types import BucketDelta, BucketKey


class InventoryRepository(Protocol):
    """Facade repo phục vụ PostingEngine và hạch toán tồn kho."""

    def lock_buckets(self, keys: list[BucketKey]) -> None:
        """Khóa các dòng stock_balance theo thứ tự chuẩn để chống race condition."""
        ...

    def get_or_create_balance(self, key: BucketKey) -> Any:
        ...

    def apply_deltas(self, deltas: list[BucketDelta]) -> None:
        ...

    def append_movement(self, movement: Any) -> None:
        ...


class CatalogRepository(Protocol):
    def get_product(self, product_id: UUID) -> Any | None:
        ...

    def resolve_barcode(self, barcode: str) -> Any | None:
        ...


class WarehouseRepository(Protocol):
    def lock_warehouse(self, warehouse_id: UUID) -> None:
        ...

    def get_location(self, location_id: UUID) -> Any | None:
        ...

    def is_location_frozen(self, location_id: UUID) -> bool:
        ...


class OrderRepository(Protocol):
    def load_order(self, order_id: UUID) -> Any | None:
        ...

    def lock_order(self, order_id: UUID) -> None:
        ...


class DocumentRepository(Protocol):
    def load_document(self, document_id: UUID) -> Any | None:
        ...

    def save_draft(self, document: Any) -> UUID:
        ...

    def mark_posted(self, document_id: UUID, posted_at: datetime) -> None:
        ...


class StocktakeRepository(Protocol):
    def load_active_count(self, location_id: UUID) -> Any | None:
        ...

    def save_counts(self, stocktake_id: UUID, counts: list[Any]) -> None:
        ...


class AuditRepository(Protocol):
    def append(self, event: Any) -> None:
        ...


class QueryRepository(Protocol):
    """Read-only queries trả DTO trực tiếp cho UI hoặc Export."""

    def get_stock_page(
        self, warehouse_id: UUID | None, search: str | None, offset: int, limit: int
    ) -> tuple[list[dict[str, Any]], int]:
        ...

    def trace_lot(self, lot_code: str) -> dict[str, Any]:
        ...

    def reconcile_ledger(self, as_of: datetime | None) -> dict[str, Any]:
        ...


class IdentityRepository(Protocol):
    def get_user_by_username(self, username: str) -> Any | None:
        ...

    def get_user_roles(self, user_id: UUID) -> list[str]:
        ...
