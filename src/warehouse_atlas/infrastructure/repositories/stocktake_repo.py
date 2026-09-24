from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from warehouse_atlas.infrastructure.orm.stocktake_models import Stocktake as StocktakeRow


class SqlAlchemyStocktakeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def load_active_count(self, location_id: UUID) -> StocktakeRow | None:
        stmt = select(StocktakeRow).where(
            StocktakeRow.location_id == location_id,
            StocktakeRow.status.in_(["COUNTING", "REVIEW"]),
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def save_counts(self, stocktake_id: UUID, counts: list[Any]) -> None:
        pass
