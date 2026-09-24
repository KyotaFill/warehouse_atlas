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
from warehouse_atlas.infrastructure.db.connection import (  # noqa: E402
    get_db_session,
)
from warehouse_atlas.infrastructure.orm.catalog_models import (  # noqa: E402
    Product,
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

        # File tĩnh mặc định (HTML, CSS, JS, Images, Fonts)
        super().do_GET()


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
