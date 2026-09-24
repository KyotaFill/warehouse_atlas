from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import text

from warehouse_atlas.infrastructure.db.connection import get_db_session


@dataclass(frozen=True, slots=True)
class DiscrepancyItem:
    product_id: UUID
    location_id: UUID
    lot_id: UUID
    condition: str
    balance_on_hand: Decimal
    ledger_on_hand: Decimal
    qty_difference: Decimal
    balance_reserved: Decimal
    calculated_reserved: Decimal
    reserved_difference: Decimal


@dataclass(frozen=True, slots=True)
class ReconciliationReport:
    as_of: datetime
    is_healthy: bool
    total_checked_buckets: int
    discrepancy_count: int
    discrepancies: tuple[DiscrepancyItem, ...]


class ReconciliationService:
    """
    Dịch vụ đối soát sổ kho độc lập (Inventory Reconciliation Service):
    - Đọc từ view v_inventory_reconciliation.
    - So sánh trực tiếp giữa Sổ cái Movement và Số dư StockBalance.
    - Phát hiện bất kỳ độ lệch hoặc cấp phát sai số lượng.
    """

    @classmethod
    def run_reconciliation(cls) -> ReconciliationReport:
        as_of = datetime.now(UTC)
        query = text("""
            SELECT
                product_id,
                location_id,
                lot_id,
                condition,
                balance_on_hand,
                ledger_on_hand,
                qty_difference,
                balance_reserved,
                calculated_reserved,
                reserved_difference
            FROM v_inventory_reconciliation;
        """)

        with get_db_session() as session:
            rows = session.execute(query).fetchall()

        discrepancies: list[DiscrepancyItem] = []
        for r in rows:
            if r.qty_difference != Decimal("0") or r.reserved_difference != Decimal("0"):
                discrepancies.append(
                    DiscrepancyItem(
                        product_id=r.product_id,
                        location_id=r.location_id,
                        lot_id=r.lot_id,
                        condition=r.condition,
                        balance_on_hand=r.balance_on_hand,
                        ledger_on_hand=r.ledger_on_hand,
                        qty_difference=r.qty_difference,
                        balance_reserved=r.balance_reserved,
                        calculated_reserved=r.calculated_reserved,
                        reserved_difference=r.reserved_difference,
                    )
                )

        return ReconciliationReport(
            as_of=as_of,
            is_healthy=(len(discrepancies) == 0),
            total_checked_buckets=len(rows),
            discrepancy_count=len(discrepancies),
            discrepancies=tuple(discrepancies),
        )
