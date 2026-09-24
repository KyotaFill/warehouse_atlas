from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from warehouse_atlas.infrastructure.orm.warehouse_models import (
    Location as LocationRow,
)
from warehouse_atlas.infrastructure.orm.warehouse_models import (
    Warehouse as WarehouseRow,
)


class SqlAlchemyWarehouseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def lock_warehouse(self, warehouse_id: UUID) -> None:
        stmt = select(WarehouseRow).where(WarehouseRow.id == warehouse_id).with_for_update()
        self.session.execute(stmt).scalar_one()

    def get_location(self, location_id: UUID) -> LocationRow | None:
        stmt = select(LocationRow).where(LocationRow.id == location_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def is_location_frozen(self, location_id: UUID) -> bool:
        loc = self.get_location(location_id)
        return loc.is_active is False if loc else False
