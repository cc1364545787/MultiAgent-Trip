from typing import Any, Literal

from pydantic import BaseModel, Field


EventType = Literal[
    "run_started",
    "status",
    "node_start",
    "node_end",
    "reasoning",
    "plan",
    "tool_call",
    "tool_result",
    "validation",
    "retry",
    "itinerary",
    "error",
    "done",
]


class StreamEvent(BaseModel):
    type: EventType
    node: str | None = None
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
