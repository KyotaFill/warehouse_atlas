from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ToolCallRequest:
    id: str
    tool_name: str
    arguments: dict[str, Any]


@dataclass(frozen=True, slots=True)
class LLMResponse:
    content: str
    tool_calls: tuple[ToolCallRequest, ...] = ()


class LLMPort(Protocol):
    """Port giao tiếp LLM (Ollama) có hỗ trợ gọi tool có kiểm soát."""

    def generate(
        self,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
    ) -> LLMResponse:
        ...
