import tkinter as tk
from tkinter import ttk

from sqlalchemy import select

from warehouse_atlas.infrastructure.db.connection import get_db_session
from warehouse_atlas.infrastructure.orm.catalog_models import Product
from warehouse_atlas.infrastructure.orm.inventory_models import StockBalance
from warehouse_atlas.infrastructure.orm.lot_models import Lot
from warehouse_atlas.infrastructure.orm.warehouse_models import Location
from warehouse_atlas.presentation.theme.tokens import ThemeTokens


class StockView(ttk.Frame):
    """Màn hình xem tồn kho (Stock Balances Projection)."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=ThemeTokens.SPACE.MD, pady=ThemeTokens.SPACE.MD)

        # Header bar
        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(0, ThemeTokens.SPACE.MD))

        title = ttk.Label(
            header,
            text="Tồn Kho Thực Tế Theo Lô & Vị Trí",
            font=(
                ThemeTokens.FONT.FONT_FAMILY,
                ThemeTokens.FONT.SIZE_HEADER,
                ThemeTokens.FONT.WEIGHT_BOLD,
            ),
        )
        title.pack(side=tk.LEFT)

        btn_reload = ttk.Button(header, text="Làm mới", command=self.load_data)
        btn_reload.pack(side=tk.RIGHT)

        # Table frame
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = (
            "sku",
            "name",
            "location",
            "lot",
            "expiry",
            "condition",
            "on_hand",
            "reserved",
            "free_qty",
        )
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("sku", text="Mã SKU")
        self.tree.heading("name", text="Tên Sản Phẩm")
        self.tree.heading("location", text="Vị Trí")
        self.tree.heading("lot", text="Mã Lô")
        self.tree.heading("expiry", text="Hạn Dùng")
        self.tree.heading("condition", text="Tình Trạng")
        self.tree.heading("on_hand", text="Tồn Vật Lý")
        self.tree.heading("reserved", text="Đang Giữ")
        self.tree.heading("free_qty", text="Khả Dụng")

        self.tree.column("sku", width=120, anchor=tk.W)
        self.tree.column("name", width=260, anchor=tk.W)
        self.tree.column("location", width=90, anchor=tk.CENTER)
        self.tree.column("lot", width=140, anchor=tk.W)
        self.tree.column("expiry", width=100, anchor=tk.CENTER)
        self.tree.column("condition", width=90, anchor=tk.CENTER)
        self.tree.column("on_hand", width=90, anchor=tk.E)
        self.tree.column("reserved", width=90, anchor=tk.E)
        self.tree.column("free_qty", width=90, anchor=tk.E)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_data()

    def load_data(self) -> None:
        """Đọc projection số dư từ stock_balance trong PostgreSQL."""
        for item in self.tree.get_children():
            self.tree.delete(item)

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
                    )
                    .join(Product, StockBalance.product_id == Product.id)
                    .join(Location, StockBalance.location_id == Location.id)
                    .join(Lot, StockBalance.lot_id == Lot.id)
                    .order_by(Product.sku, Location.code)
                )
                rows = session.execute(stmt).all()

                for row in rows:
                    free_qty = row.on_hand - row.reserved
                    self.tree.insert(
                        "",
                        tk.END,
                        values=(
                            row.sku,
                            row.name,
                            row.location_code,
                            row.lot_code,
                            str(row.expires_on) if row.expires_on else "Không hạn",
                            row.condition,
                            f"{row.on_hand:,.0f}",
                            f"{row.reserved:,.0f}",
                            f"{free_qty:,.0f}",
                        ),
                    )
        except Exception as e:
            print(f"Lỗi tải tồn kho: {e}")
