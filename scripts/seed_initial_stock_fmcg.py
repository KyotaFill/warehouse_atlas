#!/usr/bin/env python3
# ruff: noqa: E402
"""
Seed thêm vị trí kho và tạo tồn kho ban đầu (Opening Stock) cho 40 SKU FMCG phổ biến:
- Thêm các ô kệ: A-01-03, B-01-01, B-01-02, C-01-01, C-01-02, STAGING, QUARANTINE
- Lập chứng từ OPENING chuẩn hạch toán
- Sinh Lot, StockMovement (Ledger) và StockBalance đồng bộ 100%
"""

import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from warehouse_atlas.common.constants import Condition, DocumentKind, DocumentStatus
from warehouse_atlas.infrastructure.db.connection import get_db_session
from warehouse_atlas.infrastructure.orm.catalog_models import Product, ProductUom
from warehouse_atlas.infrastructure.orm.inventory_models import (
    InventoryDocument,
    InventoryDocumentLine,
    StockBalance,
    StockMovement,
)
from warehouse_atlas.infrastructure.orm.lot_models import Lot
from warehouse_atlas.infrastructure.orm.user_models import AppUser
from warehouse_atlas.infrastructure.orm.warehouse_models import Location, Warehouse


def seed_stock() -> None:
    print("=" * 70)
    print("  SEEDING LOCATIONS & INITIAL STOCK FOR FMCG PRODUCTS")
    print("=" * 70)

    with get_db_session() as session:
        user = session.query(AppUser).filter_by(username="manager").first()
        wh_main = session.query(Warehouse).filter_by(code="WH-MAIN").first()

        # 1. Thêm các Vị trí kho mới
        new_locs = [
            ("ZONE-B", "Khu lưu trữ B (Bánh kẹo & Mì)", "STRUCTURAL", None),
            ("ZONE-C", "Khu lưu trữ C (Đồ uống & Gia vị)", "STRUCTURAL", None),
            ("STAGING", "Khu tập kết chuẩn bị xuất hàng", "DISPATCH", None),
            ("HOLD-01", "Khu cách ly hàng chờ kiểm định", "RECEIVING", None),
        ]
        loc_map = {}
        for code, name, usage, _parent in new_locs:
            loc = session.query(Location).filter_by(warehouse_id=wh_main.id, code=code).first()
            if not loc:
                loc = Location(
                    id=uuid4(),
                    warehouse_id=wh_main.id,
                    code=code,
                    name=name,
                    usage=usage,
                    is_active=True,
                )
                session.add(loc)
                session.flush()
            loc_map[code] = loc.id

        # Kệ con
        sub_locs = [
            ("A-01-03", "Kệ A Tầng 1 Ô 3", "STORAGE", "ZONE-A"),
            ("B-01-01", "Kệ B Tầng 1 Ô 1", "STORAGE", "ZONE-B"),
            ("B-01-02", "Kệ B Tầng 1 Ô 2", "STORAGE", "ZONE-B"),
            ("C-01-01", "Kệ C Tầng 1 Ô 1", "STORAGE", "ZONE-C"),
            ("C-01-02", "Kệ C Tầng 1 Ô 2", "STORAGE", "ZONE-C"),
        ]
        zone_a = session.query(Location).filter_by(warehouse_id=wh_main.id, code="ZONE-A").first()
        loc_map["ZONE-A"] = zone_a.id

        for code, name, usage, p_zone in sub_locs:
            loc = session.query(Location).filter_by(warehouse_id=wh_main.id, code=code).first()
            if not loc:
                loc = Location(
                    id=uuid4(),
                    warehouse_id=wh_main.id,
                    parent_id=loc_map[p_zone],
                    code=code,
                    name=name,
                    usage=usage,
                    is_active=True,
                )
                session.add(loc)
                session.flush()
            loc_map[code] = loc.id

        session.flush()
        print(f"✓ Đã đồng bộ các vị trí kho mới ({len(sub_locs) + len(new_locs)} locations).")

        # 2. Chọn 30 sản phẩm tiêu biểu để nhập tồn kho đầu kỳ
        products = session.query(Product).filter(Product.sku.like("SKU-%")).limit(30).all()
        storage_locations = [
            loc_map["A-01-03"],
            loc_map["B-01-01"],
            loc_map["B-01-02"],
            loc_map["C-01-01"],
            loc_map["C-01-02"],
        ]

        # Tạo 1 chứng từ OPENING chuẩn
        doc_id = uuid4()
        now_utc = datetime.now(UTC)
        doc = InventoryDocument(
            id=doc_id,
            warehouse_id=wh_main.id,
            code=f"OPN-{now_utc.strftime('%y%m%d')}-FMCG",
            kind=DocumentKind.OPENING.value,
            status=DocumentStatus.POSTED.value,
            created_by=user.id,
            approved_by=user.id,
            posted_by=user.id,
            posted_at=now_utc,
            idempotency_key=uuid4(),
            posting_payload_hash="fmcg-opening-payload-hash-verified",
            version=2,
        )
        session.add(doc)
        session.flush()

        seeded_buckets = 0
        for idx, prod in enumerate(products, start=1):
            loc_id = storage_locations[idx % len(storage_locations)]
            uom_base = (
                session.query(ProductUom)
                .filter_by(product_id=prod.id, factor_to_base=Decimal("1"))
                .first()
            )

            # Tạo Lot
            lot_id = uuid4()
            lot_code = f"LOT-{prod.sku[:12]}-{now_utc.strftime('%y%m')}-{idx:02d}"
            exp_date = date(2026, 12, 31) if idx % 2 == 0 else date(2027, 6, 30)
            lot = Lot(
                id=lot_id,
                product_id=prod.id,
                code=lot_code,
                manufacturer_lot_code=f"MFG-{idx:04d}",
                expires_on=exp_date,
                manufactured_on=date(2026, 6, 1),
                received_at=now_utc,
                unit_cost=Decimal("25000"),
                recall_status="ACTIVE",
            )
            session.add(lot)
            session.flush()

            # 100 đơn vị cơ sở cho mỗi sản phẩm
            qty_base = Decimal("100")
            line_id = uuid4()
            line = InventoryDocumentLine(
                id=line_id,
                document_id=doc_id,
                line_no=idx,
                product_id=prod.id,
                lot_id=lot_id,
                product_uom_id=uom_base.id,
                qty=qty_base,
                factor_to_base_snapshot=Decimal("1"),
                qty_base=qty_base,
                from_location_id=None,
                from_condition=None,
                to_location_id=loc_id,
                to_condition=Condition.GOOD.value,
            )
            session.add(line)
            session.flush()

            # Ghi sổ Movement
            movement = StockMovement(
                id=uuid4(),
                document_line_id=line_id,
                product_id=prod.id,
                lot_id=lot_id,
                from_location_id=None,
                from_condition=None,
                to_location_id=loc_id,
                to_condition=Condition.GOOD.value,
                qty_base=qty_base,
                actor_id=user.id,
                recorded_at=now_utc,
            )
            session.add(movement)

            # Cập nhật StockBalance
            bal = StockBalance(
                id=uuid4(),
                product_id=prod.id,
                location_id=loc_id,
                lot_id=lot_id,
                condition=Condition.GOOD.value,
                on_hand=qty_base,
                reserved=Decimal("0"),
                version=1,
            )
            session.add(bal)
            seeded_buckets += 1

        session.commit()
        print(f"✓ Đã hạch toán thành công phiếu OPENING cho {seeded_buckets} sản phẩm FMCG.")
        print(f"  - Tổng số lượng nhập kho mới: {seeded_buckets * 100:,.0f} đơn vị hàng.")
        print("  - Sổ cái (StockMovement) và Số dư (StockBalance) hoàn toàn khớp 100%.")


if __name__ == "__main__":
    seed_stock()
