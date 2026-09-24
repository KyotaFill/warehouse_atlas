import tkinter as tk
from tkinter import messagebox

from warehouse_atlas.presentation.theme.tokens import ThemeTokens
from warehouse_atlas.presentation.views.stock_view import StockView


class AppShell(tk.Tk):
    """Khung điều hướng chính (Desktop AppShell) của Warehouse Atlas."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Warehouse Atlas — Hệ Thống Điều Hành Kho Thông Minh")
        self.geometry(
            f"{ThemeTokens.LAYOUT.TARGET_WINDOW_WIDTH}x{ThemeTokens.LAYOUT.TARGET_WINDOW_HEIGHT}"
        )
        self.minsize(ThemeTokens.LAYOUT.MIN_WINDOW_WIDTH, ThemeTokens.LAYOUT.MIN_WINDOW_HEIGHT)
        self.configure(bg=ThemeTokens.COLOR.BG_MAIN)

        self._build_top_bar()
        self._build_main_layout()

    def _build_top_bar(self) -> None:
        top_bar = tk.Frame(self, bg=ThemeTokens.COLOR.ACTION_PRIMARY, height=52)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        lbl_logo = tk.Label(
            top_bar,
            text="WAREHOUSE ATLAS",
            fg=ThemeTokens.COLOR.TEXT_INVERSE,
            bg=ThemeTokens.COLOR.ACTION_PRIMARY,
            font=(ThemeTokens.FONT.FONT_FAMILY, 13, ThemeTokens.FONT.WEIGHT_BOLD),
            padx=ThemeTokens.SPACE.MD,
        )
        lbl_logo.pack(side=tk.LEFT, pady=ThemeTokens.SPACE.SM)

        lbl_wh = tk.Label(
            top_bar,
            text="📍 Kho: WH-MAIN (Tổng kho HCM)",
            fg="#D6E4FF",
            bg=ThemeTokens.COLOR.ACTION_PRIMARY,
            font=(ThemeTokens.FONT.FONT_FAMILY, 10),
            padx=ThemeTokens.SPACE.SM,
        )
        lbl_wh.pack(side=tk.LEFT)

        lbl_user = tk.Label(
            top_bar,
            text="👤 Nguyễn Nhận Hàng (OPERATOR)",
            fg=ThemeTokens.COLOR.TEXT_INVERSE,
            bg=ThemeTokens.COLOR.ACTION_PRIMARY,
            font=(ThemeTokens.FONT.FONT_FAMILY, 10),
            padx=ThemeTokens.SPACE.MD,
        )
        lbl_user.pack(side=tk.RIGHT, pady=ThemeTokens.SPACE.SM)

    def _build_main_layout(self) -> None:
        body = tk.Frame(self, bg=ThemeTokens.COLOR.BG_MAIN)
        body.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        sidebar = tk.Frame(
            body, bg=ThemeTokens.COLOR.SURFACE, width=ThemeTokens.LAYOUT.SIDEBAR_WIDTH
        )
        sidebar.pack(
            side=tk.LEFT, fill=tk.Y, padx=(ThemeTokens.SPACE.SM, 0), pady=ThemeTokens.SPACE.SM
        )
        sidebar.pack_propagate(False)

        nav_items = [
            ("📦 Tồn Kho Thực Tế", self._show_stock),
            ("📥 Nhập Kho Lô Hàng", self._show_receipt_placeholder),
            ("📤 Xuất Kho & Đơn Bán", self._show_shipment_placeholder),
            ("🔍 Kiểm Kê Mù", self._show_stocktake_placeholder),
            ("🗺️ Sơ Đồ Kho 2D", self._show_map_placeholder),
            ("🤖 Trợ Lý Trí Tuệ Nhân Tạo", self._show_ai_placeholder),
        ]

        for text, cmd in nav_items:
            btn = tk.Button(
                sidebar,
                text=text,
                command=cmd,
                anchor=tk.W,
                padx=ThemeTokens.SPACE.MD,
                pady=10,
                relief="flat",
                bg=ThemeTokens.COLOR.SURFACE,
                fg=ThemeTokens.COLOR.TEXT_PRIMARY,
                font=(ThemeTokens.FONT.FONT_FAMILY, 11),
                cursor="hand2",
            )
            btn.pack(fill=tk.X, pady=2)

        # Content Container
        self.content_container = tk.Frame(body, bg=ThemeTokens.COLOR.SURFACE)
        self.content_container.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=ThemeTokens.SPACE.SM,
            pady=ThemeTokens.SPACE.SM,
        )

        # Mặc định mở màn hình Tồn kho
        self._current_view = None
        self._show_stock()

    def _switch_view(self, view_cls) -> None:
        if self._current_view is not None:
            self._current_view.destroy()
        self._current_view = view_cls(self.content_container)

    def _show_stock(self) -> None:
        self._switch_view(StockView)

    def _show_receipt_placeholder(self) -> None:
        messagebox.showinfo(
            "Nhập Kho", "Tính năng Nhập Kho (P0 vertical slice) đã sẵn sàng qua backend service."
        )

    def _show_shipment_placeholder(self) -> None:
        messagebox.showinfo("Xuất Kho", "Tính năng Giữ hàng & Xuất kho theo FEFO (P0 Tuần 3).")

    def _show_stocktake_placeholder(self) -> None:
        messagebox.showinfo("Kiểm Kê", "Tính năng Kiểm kê mù & Đóng băng vị trí (P0 Tuần 4).")

    def _show_map_placeholder(self) -> None:
        messagebox.showinfo("Sơ Đồ Kho", "Sơ đồ 2D Canvas & Lập lộ trình tối ưu (P1 Tuần 5).")

    def _show_ai_placeholder(self) -> None:
        messagebox.showinfo(
            "Trợ Lý AI", "Trợ lý Ollama Tool Gateway với Bằng chứng số liệu (P1 Tuần 6)."
        )
