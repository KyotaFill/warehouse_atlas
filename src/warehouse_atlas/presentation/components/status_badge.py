import tkinter as tk
from tkinter import ttk

from warehouse_atlas.presentation.theme.tokens import ThemeTokens


class StatusBadge(ttk.Frame):
    """
    Component huy hiệu trạng thái (Status Badge) tuân thủ Design System:
    - Bắt buộc có chữ tiếng Việt, không chỉ dựa vào màu sắc.
    - Màu nền và viền đồng bộ với Semantic Tokens.
    """

    COLOR_MAP = {
        "POSTED": (ThemeTokens.COLOR.SUCCESS, ThemeTokens.COLOR.SUCCESS_BG, "ĐÃ GHI SỔ"),
        "APPROVED": (ThemeTokens.COLOR.INFO, ThemeTokens.COLOR.INFO_BG, "ĐÃ DUYỆT"),
        "DRAFT": (ThemeTokens.COLOR.TEXT_MUTED, "#EDF0F2", "BẢN NHÁP"),
        "CANCELLED": (ThemeTokens.COLOR.DANGER, ThemeTokens.COLOR.DANGER_BG, "ĐÃ HỦY"),
        "GOOD": (ThemeTokens.COLOR.SUCCESS, ThemeTokens.COLOR.SUCCESS_BG, "TỐT"),
        "QUARANTINE": (ThemeTokens.COLOR.WARNING, ThemeTokens.COLOR.WARNING_BG, "CHỜ KIỂM ĐỊNH"),
        "DAMAGED": (ThemeTokens.COLOR.DANGER, ThemeTokens.COLOR.DANGER_BG, "HƯ HỎNG"),
    }

    def __init__(self, parent: tk.Widget, status: str, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        fg, bg, label_text = self.COLOR_MAP.get(
            status.upper(),
            (ThemeTokens.COLOR.TEXT_PRIMARY, ThemeTokens.COLOR.BG_MAIN, status),
        )

        label = tk.Label(
            self,
            text=f" {label_text} ",
            fg=fg,
            bg=bg,
            font=(ThemeTokens.FONT.FONT_FAMILY, 9, ThemeTokens.FONT.WEIGHT_BOLD),
            padx=ThemeTokens.SPACE.XXS,
            pady=2,
            relief="solid",
            borderwidth=1,
        )
        label.pack()
