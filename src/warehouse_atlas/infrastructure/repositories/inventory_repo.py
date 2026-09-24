from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from warehouse_atlas.common.exceptions import InsufficientStockError
from warehouse_atlas.common.types import BucketDelta, BucketKey
from warehouse_atlas.infrastructure.orm.inventory_models import (
    StockBalance as StockBalanceRow,
)
from warehouse_atlas.infrastructure.orm.inventory_models import (
    StockMovement as StockMovementRow,
)


class SqlAlchemyInventoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def lock_buckets(self, keys: list[BucketKey]) -> None:
        """
        Khóa các dòng stock_balance theo thứ tự khóa tăng dần để chống deadlock.
        Nếu dòng chưa tồn tại trong DB, tạo mới với on_hand=0, reserved=0 rồi khóa.
        """
        if not keys:
            return

        sorted_keys = sorted(
            keys,
            key=lambda k: (str(k.product_id), str(k.location_id), str(k.lot_id), k.condition.value),
        )

        for key in sorted_keys:
            stmt = (
                select(StockBalanceRow)
                .where(
                    StockBalanceRow.product_id == key.product_id,
                    StockBalanceRow.location_id == key.location_id,
                    StockBalanceRow.lot_id == key.lot_id,
                    StockBalanceRow.condition == key.condition.value,
                )
                .with_for_update()
            )
            row = self.session.execute(stmt).scalar_one_or_none()
            if row is None:
                # Tạo bản ghi số dư 0 ban đầu
                new_balance = StockBalanceRow(
                    id=uuid4(),
                    product_id=key.product_id,
                    location_id=key.location_id,
                    lot_id=key.lot_id,
                    condition=key.condition.value,
                    on_hand=Decimal("0"),
                    reserved=Decimal("0"),
                    version=1,
                )
                self.session.add(new_balance)
                self.session.flush()
                # Khóa lại dòng vừa tạo
                self.session.execute(stmt).scalar_one()

    def apply_deltas(self, deltas: list[BucketDelta]) -> None:
        """Áp dụng biến động số dư và kiểm tra chặt chẽ điều kiện tồn âm."""
        for delta in deltas:
            key = delta.key
            stmt = select(StockBalanceRow).where(
                StockBalanceRow.product_id == key.product_id,
                StockBalanceRow.location_id == key.location_id,
                StockBalanceRow.lot_id == key.lot_id,
                StockBalanceRow.condition == key.condition.value,
            )
            row = self.session.execute(stmt).scalar_one()

            new_on_hand = row.on_hand + delta.delta_on_hand
            new_reserved = row.reserved + delta.delta_reserved

            if new_on_hand < Decimal("0"):
                raise InsufficientStockError(
                    f"Tồn kho không đủ tại vị trí {key.location_id}: hiện có {row.on_hand}, cần giảm {abs(delta.delta_on_hand)}"
                )
            if new_reserved < Decimal("0"):
                raise InsufficientStockError(f"Reserved không được âm: {new_reserved}")
            if new_reserved > new_on_hand:
                raise InsufficientStockError(
                    f"Reserved ({new_reserved}) vượt quá on_hand ({new_on_hand})"
                )

            row.on_hand = new_on_hand
            row.reserved = new_reserved
            row.version += 1
            self.session.flush()

    def append_movement(self, movement: Any) -> None:
        """Ghi nhận biến động sổ kho bất biến."""
        row = StockMovementRow(
            id=uuid4(),
            document_line_id=movement.document_line_id,
            product_id=movement.product_id,
            lot_id=movement.lot_id,
            from_location_id=movement.from_location_id,
            from_condition=movement.from_condition.value if movement.from_condition else None,
            to_location_id=movement.to_location_id,
            to_condition=movement.to_condition.value if movement.to_condition else None,
            qty_base=movement.quantity,
            reverses_movement_id=None,
            actor_id=movement.actor_id,
            recorded_at=movement.recorded_at,
        )
        self.session.add(row)
        self.session.flush()
