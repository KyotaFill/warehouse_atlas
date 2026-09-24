import queue
import threading
import uuid
from collections.abc import Callable
from typing import Any

from warehouse_atlas.common.exceptions import AppError
from warehouse_atlas.presentation.workers.task_result import TaskResult


class BackgroundTaskRunner:
    """
    Điều phối các tác vụ ngầm (Background Worker) cho Tkinter:
    - Chạy tác vụ DB, thuật toán route hoặc LLM ở thread riêng để không block Tkinter UI loop.
    - Đẩy TaskResult vào queue.
    - Main thread định kỳ kiểm tra kết quả qua Tkinter after().
    """

    def __init__(self, check_interval_ms: int = 50) -> None:
        self._queue: queue.Queue[tuple[TaskResult[Any], Callable[[TaskResult[Any]], None]]] = (
            queue.Queue()
        )
        self._check_interval_ms = check_interval_ms
        self._active_tokens: set[str] = set()

    def submit(
        self,
        task_fn: Callable[..., Any],
        on_complete: Callable[[TaskResult[Any]], None],
        *args: Any,
        **kwargs: Any,
    ) -> str:
        task_id = str(uuid.uuid4())
        self._active_tokens.add(task_id)

        def worker() -> None:
            try:
                result_data = task_fn(*args, **kwargs)
                task_res = TaskResult(
                    task_id=task_id,
                    is_success=True,
                    data=result_data,
                )
            except AppError as e:
                task_res = TaskResult(
                    task_id=task_id,
                    is_success=False,
                    error_message=e.message,
                    error_code=e.code,
                )
            except Exception as e:
                task_res = TaskResult(
                    task_id=task_id,
                    is_success=False,
                    error_message=f"Lỗi không xác định: {e!s}",
                    error_code="UNKNOWN_ERROR",
                )

            self._queue.put((task_res, on_complete))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return task_id

    def cancel(self, task_id: str) -> None:
        """Đánh dấu hủy/bỏ qua kết quả task đã cũ khi người dùng chuyển màn."""
        self._active_tokens.discard(task_id)

    def attach_tk_root(self, root: Any) -> None:
        """Gắn vòng lặp polling vào Tkinter root bằng after()."""

        def poll() -> None:
            while not self._queue.empty():
                try:
                    task_res, callback = self._queue.get_nowait()
                    if task_res.task_id in self._active_tokens:
                        self._active_tokens.remove(task_res.task_id)
                        callback(task_res)
                except queue.Empty:
                    break
            root.after(self._check_interval_ms, poll)

        root.after(self._check_interval_ms, poll)
