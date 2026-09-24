from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select

from warehouse_atlas.application.dtos.inventory_dto import PostDocumentCommand
from warehouse_atlas.application.services.posting_engine import PostingEngine
from warehouse_atlas.common.constants import Condition, DocumentKind, DocumentStatus
from warehouse_atlas.domain.model.document import InventoryDocument, InventoryDocumentLine
from warehouse_atlas.infrastructure.db.connection import get_db_session
from warehouse_atlas.infrastructure.orm.catalog_models import Product, ProductUom
from warehouse_atlas.infrastructure.orm.inventory_models import (
    InventoryDocument as InventoryDocumentRow,
)
from warehouse_atlas.infrastructure.orm.inventory_models import (
    InventoryDocumentLine as InventoryDocumentLineRow,
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
from warehouse_atlas.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def test_vertical_slice_receipt_posting_to_postgres():
    """
    Test cổng nghiệm thu Tuần 1:
    Tạo SKU / Lô -> Nhận hàng (Receipt) -> Ghi sổ (PostingEngine + UnitOfWork)
    -> Kiểm tra đúng 10 món trong StockBalance và bản ghi sổ StockMovement trên PostgreSQL.
    """
    with get_db_session() as session:
        # Lấy dữ liệu đã seed
        user = session.execute(select(AppUser).where(AppUser.username == "receiver")).scalar_one()
        product = session.execute(select(Product).where(Product.sku == "SKU-MILK-1L")).scalar_one()
        wh = session.execute(select(Warehouse).where(Warehouse.code == "WH-MAIN")).scalar_one()
        loc_storage = session.execute(
            select(Location).where(Location.code == "A-01-01")
        ).scalar_one()
        uom_base = session.execute(
            select(ProductUom).where(
                ProductUom.product_id == product.id, ProductUom.factor_to_base == Decimal("1")
            )
        ).scalar_one()

        # Tạo Lô hàng mới (Internal Lot)
        lot_id = uuid4()
        lot_row = LotRow(
            id=lot_id,
            product_id=product.id,
            code=f"LOT-TEST-{str(uuid4())[:8]}",
            manufacturer_lot_code="MFG-2026-X",
            expires_on=date(2026, 12, 31),
            received_at=datetime.now(UTC),
            unit_cost=Decimal("25000"),
            recall_status="ACTIVE",
        )
        session.add(lot_row)
        session.flush()

        # Tạo chứng từ nhập kho (Receipt) trong DB
        doc_id = uuid4()
        line_id = uuid4()
        qty_to_receive = Decimal("10")

        doc_row = InventoryDocumentRow(
            id=doc_id,
            warehouse_id=wh.id,
            code=f"REC-{str(uuid4())[:8]}",
            kind=DocumentKind.RECEIPT.value,
            status=DocumentStatus.APPROVED.value,
            created_by=user.id,
            version=1,
        )
        session.add(doc_row)
        session.flush()

        line_row = InventoryDocumentLineRow(
            id=line_id,
            document_id=doc_id,
            line_no=1,
            product_id=product.id,
            lot_id=lot_id,
            product_uom_id=uom_base.id,
            qty=qty_to_receive,
            factor_to_base_snapshot=Decimal("1"),
            qty_base=qty_to_receive,
            from_location_id=None,
            from_condition=None,
            to_location_id=loc_storage.id,
            to_condition=Condition.GOOD.value,
        )
        session.add(line_row)
        session.commit()

    # Thực hiện hạch toán qua PostingEngine và SqlAlchemyUnitOfWork
    uow = SqlAlchemyUnitOfWork()
    with uow:
        domain_line = InventoryDocumentLine(
            id=line_id,
            document_id=doc_id,
            line_number=1,
            product_id=product.id,
            uom_id=uom_base.id,
            quantity=qty_to_receive,
            quantity_base=qty_to_receive,
            lot_id=lot_id,
            from_location_id=None,
            to_location_id=loc_storage.id,
            from_condition=None,
            to_condition=Condition.GOOD,
        )
        domain_doc = InventoryDocument(
            id=doc_id,
            warehouse_id=wh.id,
            code=doc_row.code,
            kind=DocumentKind.RECEIPT,
            status=DocumentStatus.APPROVED,
            created_by=user.id,
            created_at=datetime.now(UTC),
            version=1,
            lines=[domain_line],
        )

        cmd = PostDocumentCommand(
            document_id=doc_id,
            expected_version=1,
            idempotency_key=uuid4(),
            actor_id=user.id,
            canonical_payload_hash="sha256-verified-payload-hash-01",
            lines=(),
        )

        PostingEngine.post_in_uow(uow, domain_doc, cmd)
        uow.commit()

    # Kiểm tra trực tiếp trên PostgreSQL:
    with get_db_session() as verify_session:
        # 1. Trạng thái chứng từ đã chuyển sang POSTED với đầy đủ metadata
        saved_doc = verify_session.execute(
            select(InventoryDocumentRow).where(InventoryDocumentRow.id == doc_id)
        ).scalar_one()
        assert saved_doc.status == DocumentStatus.POSTED.value
        assert saved_doc.posted_at is not None
        assert saved_doc.posted_by == user.id
        assert saved_doc.idempotency_key is not None
        assert saved_doc.posting_payload_hash == "sha256-verified-payload-hash-01"

        # 2. Sinh đúng 1 bản ghi sổ kho (Movement)
        movement = verify_session.execute(
            select(StockMovementRow).where(StockMovementRow.document_line_id == line_id)
        ).scalar_one()
        assert movement.qty_base == qty_to_receive
        assert movement.to_location_id == loc_storage.id
        assert movement.to_condition == Condition.GOOD.value
        assert movement.actor_id == user.id

        # 3. Số dư tồn kho StockBalance đúng bằng 10, reserved bằng 0
        balance = verify_session.execute(
            select(StockBalanceRow).where(
                StockBalanceRow.product_id == product.id,
                StockBalanceRow.location_id == loc_storage.id,
                StockBalanceRow.lot_id == lot_id,
                StockBalanceRow.condition == Condition.GOOD.value,
            )
        ).scalar_one()
        assert balance.on_hand == qty_to_receive
        assert balance.reserved == Decimal("0")
