from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from warehouse_atlas.application.ports.llm_port import ToolDefinition
from warehouse_atlas.common.exceptions import UnauthorizedError


@dataclass(frozen=True, slots=True)
class ToolEvidence:
    """Bằng chứng dữ liệu thực tế gắn kèm câu trả lời của trợ lý."""
    tool_name: str
    arguments: dict[str, Any]
    result: Any
    as_of: datetime


class ToolGateway:
    """
    Cổng kiểm soát các công cụ AI được phép gọi (Allowlist Tool Gateway):
    - Đảm bảo LLM chỉ gọi các hàm đã đăng ký trong allowlist.
    - Model không bao giờ có quyền thực thi shell hay câu lệnh SQL trực tiếp.
    - Mọi lời gọi đều sinh ra bằng chứng (evidence) và thời điểm as_of.
    """

    def __init__(self) -> None:
        self._tools: dict[str, tuple[ToolDefinition, Callable[..., Any]]] = {}

    def register(
        self,
        definition: ToolDefinition,
        handler: Callable[..., Any],
    ) -> None:
        self._tools[definition.name] = (definition, handler)

    def get_definitions(self) -> list[ToolDefinition]:
        return [defn for defn, _ in self._tools.values()]

    def execute(self, tool_name: str, arguments: dict[str, Any]) -> ToolEvidence:
        if tool_name not in self._tools:
            raise UnauthorizedError(f"Công cụ {tool_name} không nằm trong danh sách được phép", role="AI_AGENT")

        _, handler = self._tools[tool_name]
        as_of = datetime.now(timezone.utc)
        result_data = handler(**arguments)

        return ToolEvidence(
            tool_name=tool_name,
            arguments=arguments,
            result=result_data,
            as_of=as_of,
        )
