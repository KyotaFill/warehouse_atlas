from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select

from warehouse_atlas.application.services.inventory_service import InventoryService
from warehouse_atlas.application.services.reconciliation_service import ReconciliationService
from warehouse_atlas.common.constants import Condition, DocumentKind, DocumentStatus
from warehouse_atlas.common.exceptions import DomainError
from warehouse_atlas.infrastructure.db.connection import get_db_session
from warehouse_atlas.infrastructure.orm.catalog_models import Product, ProductUom
from warehouse_atlas.infrastructure.orm.inventory_models import (
    InventoryDocument as InventoryDocumentRow,
)
from warehouse_atlas.infrastructure.orm.inventory_models import (
    StockBalance as StockBalanceRow,
)
from warehouse_atlas.infrastructure.orm.inventory_models import (
    StockMovement as StockMovementRow,
)
from warehouse_atlas.infrastructure.orm.lot_models import Lot as LotRow
from warehouse_atlas.infrastructure.orm.user_models import AppUser
from warehouse_atlas.infrastructure.orm.warehouse_models import Location, Warehouse


@pytest.fixture
def test_setup():
    """Chuẩn bị sẵn 1 SKU và 1 Lô có sẵn 10 đơn vị tại ô A-01-01."""
    with get_db_session() as session:
        user = session.execute(select(AppUser).where(AppUser.username == "manager")).scalar_one()
        wh = session.execute(select(Warehouse).where(Warehouse.code == "WH-MAIN")).scalar_one()
        loc_a = session.execute(select(Location).where(Location.code == "A-01-01")).scalar_one()
        loc_b = session.execute(select(Location).where(Location.code == "A-01-02")).scalar_one()
        product = session.execute(select(Product).where(Product.sku == "SKU-MILK-1L")).scalar_one()
        uom_base = session.execute(
            select(ProductUom).where(
                ProductUom.product_id == product.id, ProductUom.factor_to_base == Decimal("1")
            )
        ).scalar_one()

        lot_id = uuid4()
        lot = LotRow(
            id=lot_id,
            product_id=product.id,
            code=f"LOT-WF-{str(uuid4())[:8]}",
            manufacturer_lot_code="MFG-TEST",
            expires_on=date(2026, 12, 31),
            received_at=datetime.now(UTC),
            unit_cost=Decimal("20000"),
            recall_status="ACTIVE",
        )
        session.add(lot)
        session.flush()

        # Tạo số dư ban đầu: 10 món tại A-01-01
        # Ghi document OPENING và movement để đối soát đúng
        doc_id = uuid4()
        doc = InventoryDocumentRow(
            id=doc_id,
            warehouse_id=wh.id,
            code=f"OPN-{str(uuid4())[:8]}",
            kind=DocumentKind.OPENING.value,
            status=DocumentStatus.POSTED.value,
            created_by=user.id,
            approved_by=user.id,
            posted_by=user.id,
            posted_at=datetime.now(UTC),
            idempotency_key=uuid4(),
            posting_payload_hash="seed-opening-hash",
            version=2,
        )
        session.add(doc)
        session.flush()

        from warehouse_atlas.infrastructure.orm.inventory_models import (
            InventoryDocumentLine as LineRow,
        )

        line_id = uuid4()
        line = LineRow(
            id=line_id,
            document_id=doc_id,
            line_no=1,
            product_id=product.id,
            lot_id=lot_id,
            product_uom_id=uom_base.id,
            qty=Decimal("10"),
            factor_to_base_snapshot=Decimal("1"),
            qty_base=Decimal("10"),
            from_location_id=None,
            from_condition=None,
            to_location_id=loc_a.id,
            to_condition=Condition.GOOD.value,
        )
        session.add(line)
        session.flush()

        movement = StockMovementRow(
            id=uuid4(),
            document_line_id=line_id,
            product_id=product.id,
            lot_id=lot_id,
            from_location_id=None,
            from_condition=None,
            to_location_id=loc_a.id,
            to_condition=Condition.GOOD.value,
            qty_base=Decimal("10"),
            actor_id=user.id,
            recorded_at=datetime.now(UTC),
        )
        session.add(movement)

        balance_a = StockBalanceRow(
            id=uuid4(),
            product_id=product.id,
            location_id=loc_a.id,
            lot_id=lot_id,
            condition=Condition.GOOD.value,
            on_hand=Decimal("10"),
            reserved=Decimal("0"),
            version=1,
        )
        session.add(balance_a)
        session.commit()

        return {
            "user_id": user.id,
            "wh_id": wh.id,
            "product_id": product.id,
            "uom_id": uom_base.id,
            "lot_id": lot_id,
            "loc_a_id": loc_a.id,
            "loc_b_id": loc_b.id,
        }


def test_transfer_preserves_total_warehouse_stock(test_setup):
    """
    Test Điều chuyển kho (Transfer):
    - Chuyển 3 hộp từ A-01-01 sang A-01-02.
    - Tổng tồn kho không đổi (=10).
    - A-01-01 còn 7, A-01-02 có 3.
    """
    ctx = test_setup
    svc = InventoryService()

    # 1. Tạo bản nháp điều chuyển 3 hộp
    items = [(ctx["product_id"], ctx["lot_id"], ctx["uom_id"], Decimal("3"), Condition.GOOD)]
    doc_id = svc.create_transfer_draft(
        warehouse_id=ctx["wh_id"],
        actor_id=ctx["user_id"],
        items=items,
        from_location_id=ctx["loc_a_id"],
        to_location_id=ctx["loc_b_id"],
    )

    # 2. Duyệt và ghi sổ
    svc.approve_document(doc_id, ctx["user_id"])
    svc.post_document(doc_id, ctx["user_id"], idempotency_key=uuid4())

    # 3. Kiểm tra số dư trên DB
    with get_db_session() as session:
        bal_a = session.execute(
            select(StockBalanceRow).where(
                StockBalanceRow.product_id == ctx["product_id"],
                StockBalanceRow.location_id == ctx["loc_a_id"],
                StockBalanceRow.lot_id == ctx["lot_id"],
            )
        ).scalar_one()
        bal_b = session.execute(
            select(StockBalanceRow).where(
                StockBalanceRow.product_id == ctx["product_id"],
                StockBalanceRow.location_id == ctx["loc_b_id"],
                StockBalanceRow.lot_id == ctx["lot_id"],
            )
        ).scalar_one()

        assert bal_a.on_hand == Decimal("7")
        assert bal_b.on_hand == Decimal("3")
        assert bal_a.on_hand + bal_b.on_hand == Decimal("10")  # Bảo toàn tổng lượng


def test_reclassify_condition_change(test_setup):
    """
    Test Chuyển đổi trạng thái (Reclassify):
    - Chuyển 2 hộp tại A-01-01 từ GOOD sang DAMAGED.
    - Bucket GOOD còn 8, Bucket DAMAGED có 2.
    """
    ctx = test_setup
    svc = InventoryService()

    doc_id = svc.create_reclassify_draft(
        warehouse_id=ctx["wh_id"],
        actor_id=ctx["user_id"],
        product_id=ctx["product_id"],
        lot_id=ctx["lot_id"],
        uom_id=ctx["uom_id"],
        location_id=ctx["loc_a_id"],
        qty=Decimal("2"),
        from_condition=Condition.GOOD,
        to_condition=Condition.DAMAGED,
        reason="Hộp bị bóp méo khi bốc dỡ",
    )

    svc.approve_document(doc_id, ctx["user_id"])
    svc.post_document(doc_id, ctx["user_id"], idempotency_key=uuid4())

    with get_db_session() as session:
        bal_good = session.execute(
            select(StockBalanceRow).where(
                StockBalanceRow.product_id == ctx["product_id"],
                StockBalanceRow.location_id == ctx["loc_a_id"],
                StockBalanceRow.lot_id == ctx["lot_id"],
                StockBalanceRow.condition == Condition.GOOD.value,
            )
        ).scalar_one()
        bal_damaged = session.execute(
            select(StockBalanceRow).where(
                StockBalanceRow.product_id == ctx["product_id"],
                StockBalanceRow.location_id == ctx["loc_a_id"],
                StockBalanceRow.lot_id == ctx["lot_id"],
                StockBalanceRow.condition == Condition.DAMAGED.value,
            )
        ).scalar_one()

        assert bal_good.on_hand == Decimal("8")
        assert bal_damaged.on_hand == Decimal("2")


def test_reversal_workflow(test_setup):
    """
    Test Bút toán đảo (Reversal Workflow):
    - Chuyển 4 hộp sang B.
    - Sau đó thực hiện bút toán đảo (Reversal).
    - Toàn bộ 4 hộp quay trở lại ô A. Lịch sử ledger lưu đầy đủ 2 movement đối ứng.
    """
    ctx = test_setup
    svc = InventoryService()

    items = [(ctx["product_id"], ctx["lot_id"], ctx["uom_id"], Decimal("4"), Condition.GOOD)]
    trf_id = svc.create_transfer_draft(
        warehouse_id=ctx["wh_id"],
        actor_id=ctx["user_id"],
        items=items,
        from_location_id=ctx["loc_a_id"],
        to_location_id=ctx["loc_b_id"],
    )
    svc.approve_document(trf_id, ctx["user_id"])
    svc.post_document(trf_id, ctx["user_id"], idempotency_key=uuid4())

    # Đảo chứng từ
    svc.reverse_document(
        document_id=trf_id,
        reason="Chuyển nhầm ô kệ",
        actor_id=ctx["user_id"],
        idempotency_key=uuid4(),
    )

    with get_db_session() as session:
        # Số dư phải quay lại y như ban đầu (A: 10, B: 0)
        bal_a = session.execute(
            select(StockBalanceRow).where(
                StockBalanceRow.product_id == ctx["product_id"],
                StockBalanceRow.location_id == ctx["loc_a_id"],
                StockBalanceRow.lot_id == ctx["lot_id"],
            )
        ).scalar_one()
        bal_b = session.execute(
            select(StockBalanceRow).where(
                StockBalanceRow.product_id == ctx["product_id"],
                StockBalanceRow.location_id == ctx["loc_b_id"],
                StockBalanceRow.lot_id == ctx["lot_id"],
            )
        ).scalar_one()

        assert bal_a.on_hand == Decimal("10")
        assert bal_b.on_hand == Decimal("0")

        # Cấm đảo lần 2 trên cùng 1 chứng từ
        with pytest.raises(DomainError):
            svc.reverse_document(
                document_id=trf_id,
                reason="Thử đảo lần 2",
                actor_id=ctx["user_id"],
                idempotency_key=uuid4(),
            )


def test_reconciliation_healthy(test_setup):
    """
    Test Đối soát số dư kho (Reconciliation):
    - Đảm bảo ReconciliationService đọc và kiểm tra 100% khớp giữa sổ cái và số dư.
    """
    report = ReconciliationService.run_reconciliation()
    assert report.is_healthy is True
    assert report.discrepancy_count == 0
    assert report.total_checked_buckets > 0


def test_idempotency_posting(test_setup):
    """
    Test Chống ghi trùng (Idempotency):
    - Gửi lại cùng idempotency_key cho một chứng từ đã post, không bị tăng số dư hai lần.
    """
    ctx = test_setup
    svc = InventoryService()
    same_key = uuid4()

    items = [(ctx["product_id"], ctx["lot_id"], ctx["uom_id"], Decimal("1"), Condition.GOOD)]
    trf_id = svc.create_transfer_draft(
        warehouse_id=ctx["wh_id"],
        actor_id=ctx["user_id"],
        items=items,
        from_location_id=ctx["loc_a_id"],
        to_location_id=ctx["loc_b_id"],
    )
    svc.approve_document(trf_id, ctx["user_id"])

    # Post lần 1
    svc.post_document(trf_id, ctx["user_id"], idempotency_key=same_key)

    # Post lại lần 2 với cùng idempotency key -> Không lỗi, không trừ tồn thêm
    svc.post_document(trf_id, ctx["user_id"], idempotency_key=same_key)

    with get_db_session() as session:
        bal_a = session.execute(
            select(StockBalanceRow).where(
                StockBalanceRow.product_id == ctx["product_id"],
                StockBalanceRow.location_id == ctx["loc_a_id"],
                StockBalanceRow.lot_id == ctx["lot_id"],
            )
        ).scalar_one()
        # Ban đầu 10, chỉ chuyển đúng 1 lần -> còn 9
        assert bal_a.on_hand == Decimal("9")
