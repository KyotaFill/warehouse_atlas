from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session

from warehouse_atlas.infrastructure.db.connection import create_session
from warehouse_atlas.infrastructure.repositories.audit_repo import SqlAlchemyAuditRepository
from warehouse_atlas.infrastructure.repositories.catalog_repo import SqlAlchemyCatalogRepository
from warehouse_atlas.infrastructure.repositories.document_repo import SqlAlchemyDocumentRepository
from warehouse_atlas.infrastructure.repositories.inventory_repo import SqlAlchemyInventoryRepository
from warehouse_atlas.infrastructure.repositories.order_repo import SqlAlchemyOrderRepository
from warehouse_atlas.infrastructure.repositories.stocktake_repo import SqlAlchemyStocktakeRepository
from warehouse_atlas.infrastructure.repositories.warehouse_repo import SqlAlchemyWarehouseRepository


class SqlAlchemyUnitOfWork:
    """
    Triển khai UnitOfWork với SQLAlchemy Session.
    Đảm bảo quy tắc: Một use case = Một UnitOfWork = Một database transaction.
    """

    def __init__(self, session: Session | None = None) -> None:
        self._session_provided = session is not None
        self.session = session or create_session()

        # Khởi tạo các repository gắn chặt với Session của transaction này
        self.inventory = SqlAlchemyInventoryRepository(self.session)
        self.catalog = SqlAlchemyCatalogRepository(self.session)
        self.warehouse = SqlAlchemyWarehouseRepository(self.session)
        self.orders = SqlAlchemyOrderRepository(self.session)
        self.documents = SqlAlchemyDocumentRepository(self.session)
        self.stocktake = SqlAlchemyStocktakeRepository(self.session)
        self.audit = SqlAlchemyAuditRepository(self.session)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()
        if not self._session_provided:
            self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
