from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    user_input: str
    intent: dict[str, Any]
    plan: list[dict[str, Any]]
    messages: Annotated[list, add_messages]
    tool_results: dict[str, Any]
    records: list[dict[str, Any]]
    validation_errors: list[str]
    retry_count: int
    itinerary: dict[str, Any] | None
    status: str
    traces: list[dict[str, Any]]
