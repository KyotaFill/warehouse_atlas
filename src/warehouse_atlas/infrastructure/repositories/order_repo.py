from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from warehouse_atlas.infrastructure.orm.order_models import (
    SalesOrder as SalesOrderRow,
)


class SqlAlchemyOrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def load_order(self, order_id: UUID) -> SalesOrderRow | None:
        stmt = select(SalesOrderRow).where(SalesOrderRow.id == order_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def lock_order(self, order_id: UUID) -> None:
        stmt = select(SalesOrderRow).where(SalesOrderRow.id == order_id).with_for_update()
        self.session.execute(stmt).scalar_one()
