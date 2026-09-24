from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ColorTokens:
    # Nền và bề mặt
    BG_MAIN: str = "#F5F7FA"
    SURFACE: str = "#FFFFFF"
    BORDER: str = "#DFE1E6"
    BORDER_FOCUSED: str = "#2457D6"

    # Màu chữ
    TEXT_PRIMARY: str = "#172B4D"
    TEXT_MUTED: str = "#6B778C"
    TEXT_INVERSE: str = "#FFFFFF"

    # Hành động chính
    ACTION_PRIMARY: str = "#2457D6"
    ACTION_HOVER: str = "#1B44AA"
    ACTION_DISABLED: str = "#A5B4D0"

    # Trạng thái ngữ nghĩa (Semantic)
    SUCCESS: str = "#18794E"
    SUCCESS_BG: str = "#EBF7F0"
    WARNING: str = "#9A6700"
    WARNING_BG: str = "#FFF8E6"
    DANGER: str = "#B42318"
    DANGER_BG: str = "#FEECEB"
    INFO: str = "#0055CC"
    INFO_BG: str = "#E9F2FF"


@dataclass(frozen=True, slots=True)
class SpacingTokens:
    XXS: int = 4
    XS: int = 8
    SM: int = 12
    MD: int = 16
    LG: int = 24
    XL: int = 32


@dataclass(frozen=True, slots=True)
class FontTokens:
    FONT_FAMILY: str = "Noto Sans"
    SIZE_BODY: int = 11
    SIZE_SUBTITLE: int = 13
    SIZE_HEADER: int = 16
    SIZE_KPI: int = 22

    WEIGHT_REGULAR: str = "normal"
    WEIGHT_BOLD: str = "bold"


@dataclass(frozen=True, slots=True)
class LayoutTokens:
    MIN_WINDOW_WIDTH: int = 1366
    MIN_WINDOW_HEIGHT: int = 768
    TARGET_WINDOW_WIDTH: int = 1440
    TARGET_WINDOW_HEIGHT: int = 900
    TABLE_ROW_HEIGHT: int = 34
    SIDEBAR_WIDTH: int = 240


class ThemeTokens:
    """Design System Token tĩnh cho toàn bộ giao diện Tkinter của Warehouse Atlas."""

    COLOR = ColorTokens()
    SPACE = SpacingTokens()
    FONT = FontTokens()
    LAYOUT = LayoutTokens()
