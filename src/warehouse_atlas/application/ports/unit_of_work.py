from types import TracebackType
from typing import Protocol, Self

from warehouse_atlas.application.ports.repositories import (
    AuditRepository,
    CatalogRepository,
    DocumentRepository,
    InventoryRepository,
    OrderRepository,
    StocktakeRepository,
    WarehouseRepository,
)


class UnitOfWork(Protocol):
    """
    Hợp đồng UnitOfWork: Đảm bảo nguyên tử tính (Atomicity) cho một use case.
    Một use case = Một UnitOfWork = Một database transaction.
    """

    inventory: InventoryRepository
    catalog: CatalogRepository
    warehouse: WarehouseRepository
    orders: OrderRepository
    documents: DocumentRepository
    stocktake: StocktakeRepository
    audit: AuditRepository

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
