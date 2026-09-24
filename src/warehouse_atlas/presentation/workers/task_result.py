from dataclasses import dataclass


@dataclass(frozen=True)
class TaskResult[T]:
    """Kết quả trả về từ BackgroundTaskRunner về main thread."""

    task_id: str
    is_success: bool
    data: T | None = None
    error_message: str | None = None
    error_code: str | None = None
