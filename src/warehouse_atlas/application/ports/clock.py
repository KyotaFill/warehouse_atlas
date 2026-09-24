from datetime import date, datetime
from typing import Protocol


class Clock(Protocol):
    """Port đồng hồ hệ thống: cho phép mock thời gian trong test mà không đổi giờ máy."""

    def now(self) -> datetime:
        ...

    def today(self) -> date:
        ...
