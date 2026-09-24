from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class TaskResult(Generic[T]):
    """Kết quả trả về từ BackgroundTaskRunner về main thread."""
    task_id: str
    is_success: bool
    data: T | None = None
    error_message: str | None = None
    error_code: str | None = None
