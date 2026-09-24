#!/usr/bin/env python3
"""
Launcher chạy giao diện nguyên bản ECOUNT ERP kết nối trực tiếp PostgreSQL 16.
Mã nguồn HTML, CSS và DOM được giữ nguyên 100% từ hệ thống gốc.
Tích hợp API endpoints nội bộ: /api/stock, /api/documents, /api/reconciliation, /api/kpis.
"""

import http.server
import json
import socketserver
import subprocess
import sys
import threading
from pathlib import Path

# Add project root and src to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from sqlalchemy import func, select  # noqa: E402

from warehouse_atlas.application.services.reconciliation_service import (  # noqa: E402
    ReconciliationService,
)
from warehouse_atlas.common.constants import Condition, DocumentKind, DocumentStatus  # noqa: E402
from warehouse_atlas.infrastructure.db.connection import (  # noqa: E402
    get_db_session,
)
from warehouse_atlas.infrastructure.orm.catalog_models import (  # noqa: E402  # noqa: E402
    Category,
    Partner,
    Product,
    ProductBarcode,
    ProductUom,
)
from warehouse_atlas.infrastructure.orm.inventory_models import (  # noqa: E402
    InventoryDocument,
    InventoryDocumentLine,
    StockBalance,
)
from warehouse_atlas.infrastructure.orm.lot_models import Lot  # noqa: E402
from warehouse_atlas.infrastructure.orm.warehouse_models import (  # noqa: E402
    Location,
    Warehouse,
)

UI_DIR = BASE_DIR / "docs" / "reference_ui"
PORT = 28080


class EcountBackendHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def log_message(self, fmt, *args):
        # Tắt bớt log HTTP để terminal gọn gàng
        pass

    def _send_json(self, data: dict | list, status_code: int = 200) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        path = self.path.split("?")[0]

        # 1. API Tồn kho thực tế
        if path == "/api/stock":
            try:
                with get_db_session() as session:
                    stmt = (
                        select(
                            Product.sku,
                            Product.name,
                            Location.code.label("location_code"),
                            Lot.code.label("lot_code"),
                            Lot.expires_on,
                            StockBalance.condition,
                            StockBalance.on_hand,
                            StockBalance.reserved,
                            Warehouse.code.label("warehouse_code"),
                        )
                        .join(Product, StockBalance.product_id == Product.id)
                        .join(Location, StockBalance.location_id == Location.id)
                        .join(Warehouse, Location.warehouse_id == Warehouse.id)
                        .join(Lot, StockBalance.lot_id == Lot.id)
                        .order_by(Product.sku, Location.code)
                    )
                    rows = session.execute(stmt).all()
                    stock_list = [
                        {
                            "sku": r.sku,
                            "name": r.name,
                            "location": r.location_code,
                            "lot": r.lot_code,
                            "expires_on": str(r.expires_on) if r.expires_on else "Không hạn",
                            "condition": r.condition,
                            "on_hand": float(r.on_hand),
                            "reserved": float(r.reserved),
                            "free_qty": float(r.on_hand - r.reserved),
                            "warehouse": r.warehouse_code,
                        }
                        for r in rows
                    ]
                self._send_json({"status": "success", "data": stock_list})
                return
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
                return

        # 2. API Danh sách chứng từ kho
        if path == "/api/documents":
            try:
                with get_db_session() as session:
                    stmt = (
                        select(
                            InventoryDocument.id,
                            InventoryDocument.code,
                            InventoryDocument.kind,
                            InventoryDocument.status,
                            InventoryDocument.created_at,
                            InventoryDocument.posted_at,
                            func.count(InventoryDocumentLine.id).label("line_count"),
                        )
                        .outerjoin(
                            InventoryDocumentLine,
                            InventoryDocument.id == InventoryDocumentLine.document_id,
                        )
                        .group_by(InventoryDocument.id)
                        .order_by(InventoryDocument.created_at.desc())
                        .limit(15)
                    )
                    rows = session.execute(stmt).all()
                    docs = [
                        {
                            "id": str(r.id),
                            "code": r.code,
                            "kind": r.kind,
                            "status": r.status,
                            "created_at": r.created_at.strftime("%d/%m/%Y %H:%M")
                            if r.created_at
                            else "",
                            "posted_at": r.posted_at.strftime("%d/%m/%Y %H:%M")
                            if r.posted_at
                            else "-",
                            "line_count": r.line_count,
                        }
                        for r in rows
                    ]
                self._send_json({"status": "success", "data": docs})
                return
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
                return

        # 3. API Đối soát toàn vẹn sổ cái (Reconciliation)
        if path == "/api/reconciliation":
            try:
                report = ReconciliationService.run_reconciliation()
                reconcile_data = {
                    "is_healthy": report.is_healthy,
                    "as_of": report.as_of.strftime("%d/%m/%Y %H:%M:%S"),
                    "total_checked_buckets": report.total_checked_buckets,
                    "discrepancy_count": report.discrepancy_count,
                    "items": [
                        {
                            "product_id": str(d.product_id),
                            "location_id": str(d.location_id),
                            "lot_id": str(d.lot_id),
                            "condition": d.condition,
                            "balance_on_hand": float(d.balance_on_hand),
                            "ledger_on_hand": float(d.ledger_on_hand),
                            "qty_difference": float(d.qty_difference),
                            "balance_reserved": float(d.balance_reserved),
                            "calculated_reserved": float(d.calculated_reserved),
                            "reserved_difference": float(d.reserved_difference),
                        }
                        for d in report.discrepancies
                    ],
                }
                self._send_json({"status": "success", "data": reconcile_data})
                return
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
                return

        # 4. API Chỉ số tổng quan (KPIs)
        if path == "/api/kpis":
            try:
                with get_db_session() as session:
                    total_on_hand = (
                        session.execute(select(func.sum(StockBalance.on_hand))).scalar() or 0
                    )
                    total_reserved = (
                        session.execute(select(func.sum(StockBalance.reserved))).scalar() or 0
                    )
                    total_skus = (
                        session.execute(select(func.count(Product.id.distinct()))).scalar() or 0
                    )
                    total_docs = (
                        session.execute(select(func.count(InventoryDocument.id))).scalar() or 0
                    )
                    report = ReconciliationService.run_reconciliation()

                kpi_data = {
                    "total_on_hand": float(total_on_hand),
                    "total_reserved": float(total_reserved),
                    "free_qty": float(total_on_hand - total_reserved),
                    "total_skus": total_skus,
                    "total_documents": total_docs,
                    "is_reconciled": report.is_healthy,
                    "reconcile_status": "KHỚP 100% (0 LỆCH)"
                    if report.is_healthy
                    else f"LỆCH {report.discrepancy_count} BUCKET",
                }
                self._send_json({"status": "success", "data": kpi_data})
                return
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
                return

        # 5. API Danh mục Mặt hàng (Items)
        if path == "/api/items":
            try:
                with get_db_session() as session:
                    stmt = (
                        select(
                            Product.id,
                            Product.sku,
                            Product.name,
                            Category.name.label("category_name"),
                            Product.track_expiry,
                            Product.min_shelf_life_days,
                            func.coalesce(func.sum(StockBalance.on_hand), 0).label("total_on_hand"),
                        )
                        .join(Category, Product.category_id == Category.id)
                        .outerjoin(StockBalance, Product.id == StockBalance.product_id)
                        .group_by(Product.id, Category.name)
                        .order_by(Product.sku)
                    )
                    rows = session.execute(stmt).all()
                    items_list = []
                    for r in rows:
                        barcode_row = session.execute(
                            select(ProductBarcode.code)
                            .join(ProductUom, ProductBarcode.product_uom_id == ProductUom.id)
                            .where(ProductUom.product_id == r.id)
                            .limit(1)
                        ).scalar_one_or_none()
                        items_list.append(
                            {
                                "id": str(r.id),
                                "sku": r.sku,
                                "name": r.name,
                                "category": r.category_name,
                                "barcode": barcode_row or "-",
                                "track_expiry": r.track_expiry,
                                "min_shelf_life_days": r.min_shelf_life_days,
                                "on_hand": float(r.total_on_hand),
                            }
                        )
                self._send_json({"status": "success", "data": items_list})
                return
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
                return

        # 6. API Danh sách Đối tác (Partners: Suppliers & Customers)
        if path == "/api/partners":
            try:
                with get_db_session() as session:
                    stmt = select(Partner).order_by(Partner.code)
                    rows = session.execute(stmt).scalars().all()
                    partners_list = [
                        {
                            "id": str(p.id),
                            "code": p.code,
                            "name": p.name,
                            "is_supplier": p.is_supplier,
                            "is_customer": p.is_customer,
                            "phone": p.phone or "-",
                            "email": p.email or "-",
                            "address": p.address or "-",
                        }
                        for p in rows
                    ]
                self._send_json({"status": "success", "data": partners_list})
                return
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
                return

        # 7. API Danh sách Vị trí kho (Locations)
        if path == "/api/locations":
            try:
                with get_db_session() as session:
                    stmt = (
                        select(
                            Location.id,
                            Location.code,
                            Location.name,
                            Location.usage,
                            Warehouse.code.label("wh_code"),
                        )
                        .join(Warehouse, Location.warehouse_id == Warehouse.id)
                        .where(Location.usage.in_(["STORAGE", "RECEIVING", "DISPATCH", "HOLD"]))
                        .order_by(Location.code)
                    )
                    rows = session.execute(stmt).all()
                    locs = [
                        {
                            "id": str(r.id),
                            "code": r.code,
                            "name": r.name,
                            "usage": r.usage,
                            "warehouse": r.wh_code,
                        }
                        for r in rows
                    ]
                self._send_json({"status": "success", "data": locs})
                return
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
                return

        # File tĩnh mặc định (HTML, CSS, JS, Images, Fonts)
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?")[0]
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            body = json.loads(post_data)
        except Exception:
            body = {}

        # 1. API Lập phiếu Nhập kho mua hàng (Goods Receipt)
        if path == "/api/receipt/create":
            try:
                from datetime import UTC, date, datetime
                from decimal import Decimal
                from uuid import UUID, uuid4

                from warehouse_atlas.application.dtos.inventory_dto import (
                    PostDocumentCommand,
                )
                from warehouse_atlas.application.services.posting_engine import PostingEngine
                from warehouse_atlas.domain.model.document import (
                    InventoryDocument,
                    InventoryDocumentLine,
                )
                from warehouse_atlas.infrastructure.orm.inventory_models import (
                    InventoryDocument as InventoryDocumentRow,
                )
                from warehouse_atlas.infrastructure.orm.inventory_models import (
                    InventoryDocumentLine as InventoryDocumentLineRow,
                )
                from warehouse_atlas.infrastructure.orm.lot_models import Lot as LotRow
                from warehouse_atlas.infrastructure.orm.user_models import AppUser
                from warehouse_atlas.infrastructure.unit_of_work import SqlAlchemyUnitOfWork

                product_id = UUID(body["product_id"])
                location_id = UUID(body["location_id"])
                qty = Decimal(str(body["quantity"]))
                lot_code = (
                    body.get("lot_code", "").strip()
                    or f"LOT-IMP-{datetime.now(UTC).strftime('%y%m%d')}-{str(uuid4())[:4]}"
                )
                mfg_lot = body.get("mfg_lot_code", "MFG-IMPORT")
                unit_cost = Decimal(str(body.get("unit_cost", 20000)))
                partner_id = UUID(body["partner_id"]) if body.get("partner_id") else None

                uow = SqlAlchemyUnitOfWork()
                with uow:
                    user = uow.session.query(AppUser).filter_by(username="receiver").first()
                    wh = uow.session.query(Warehouse).filter_by(code="WH-MAIN").first()
                    p_uom = (
                        uow.session.query(ProductUom)
                        .filter_by(product_id=product_id, factor_to_base=Decimal("1"))
                        .first()
                    )

                    # 1. Khởi tạo Lot
                    lot_id = uuid4()
                    new_lot = LotRow(
                        id=lot_id,
                        product_id=product_id,
                        code=lot_code,
                        manufacturer_lot_code=mfg_lot,
                        supplier_id=partner_id,
                        expires_on=date(2027, 6, 30),
                        manufactured_on=date(2026, 6, 1),
                        received_at=datetime.now(UTC),
                        unit_cost=unit_cost,
                        recall_status="ACTIVE",
                    )
                    uow.session.add(new_lot)
                    uow.session.flush()

                    # 2. Tạo chứng từ RECEIPT
                    doc_id = uuid4()
                    doc_code = (
                        f"REC-{datetime.now(UTC).strftime('%y%m%d')}-{str(doc_id)[:6].upper()}"
                    )
                    doc_row = InventoryDocumentRow(
                        id=doc_id,
                        warehouse_id=wh.id,
                        code=doc_code,
                        kind=DocumentKind.RECEIPT.value,
                        status=DocumentStatus.APPROVED.value,
                        partner_id=partner_id,
                        created_by=user.id,
                        version=1,
                    )
                    uow.session.add(doc_row)
                    uow.session.flush()

                    line_id = uuid4()
                    line_row = InventoryDocumentLineRow(
                        id=line_id,
                        document_id=doc_id,
                        line_no=1,
                        product_id=product_id,
                        lot_id=lot_id,
                        product_uom_id=p_uom.id,
                        qty=qty,
                        factor_to_base_snapshot=Decimal("1"),
                        qty_base=qty,
                        from_location_id=None,
                        from_condition=None,
                        to_location_id=location_id,
                        to_condition=Condition.GOOD.value,
                    )
                    uow.session.add(line_row)
                    uow.session.flush()

                    # 3. Hạch toán qua PostingEngine
                    domain_line = InventoryDocumentLine(
                        id=line_id,
                        document_id=doc_id,
                        line_number=1,
                        product_id=product_id,
                        uom_id=p_uom.id,
                        quantity=qty,
                        quantity_base=qty,
                        lot_id=lot_id,
                        from_location_id=None,
                        to_location_id=location_id,
                        from_condition=None,
                        to_condition=Condition.GOOD,
                    )
                    domain_doc = InventoryDocument(
                        id=doc_id,
                        warehouse_id=wh.id,
                        code=doc_code,
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
                        canonical_payload_hash="receipt-live-action-verified",
                        lines=(),
                    )
                    PostingEngine.post_in_uow(uow, domain_doc, cmd)
                    uow.commit()

                self._send_json(
                    {
                        "status": "success",
                        "message": f"Ghi sổ thành công phiếu nhập {doc_code}!",
                        "code": doc_code,
                    }
                )
                return
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
                return

        self._send_json({"status": "error", "message": "Endpoint not found"}, 404)


def start_server() -> socketserver.TCPServer:
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", PORT), EcountBackendHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server


def launch_native_window() -> None:
    target_url = f"http://127.0.0.1:{PORT}/index.html"
    print("=" * 70)
    print("  WAREHOUSE ATLAS — ECOUNT ERP LIVE INTEGRATED INTERFACE")
    print("  Kết nối trực tiếp PostgreSQL 16 & API Backend.")
    print(f"  URL Local Server: {target_url}")
    print("=" * 70)

    try:
        import webview

        print("-> Đang mở cửa sổ Native Desktop qua WebKit2 / PyWebView...")
        webview.create_window(
            title="ECOUNT ERP — Giao Diện Quản Trị Kho Tham Chiếu Gốc",
            url=target_url,
            width=1440,
            height=900,
            resizable=True,
            confirm_close=False,
        )
        webview.start(gui="gtk")
        return
    except Exception as e:
        print(f"-> PyWebView: {e}. Fallback sang Chrome App Mode...")

    try:
        subprocess.run(
            [
                "google-chrome",
                f"--app={target_url}",
                "--window-size=1440,900",
                "--user-data-dir=/tmp/ecount_app_profile",
            ],
            check=True,
        )
    except Exception as e_chrome:
        print(f"Lỗi khởi chạy: {e_chrome}")


def main() -> None:
    server = start_server()
    try:
        launch_native_window()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
