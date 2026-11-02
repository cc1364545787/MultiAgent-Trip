from __future__ import annotations

from typing import Any, Callable, Awaitable

from app.tools.calendar import build_calendar
from app.tools.currency import convert_currency
from app.tools.schemas import TOOL_SCHEMAS
from app.tools.search import search_travel
from app.tools.weather import get_weather

TOOL_FUNCTIONS: dict[str, Callable[..., Awaitable[Any] | Any]] = {
    "search_travel": search_travel,
    "get_weather": get_weather,
    "convert_currency": convert_currency,
    "build_calendar": build_calendar,
}


async def execute_tool(name: str, arguments: dict[str, Any]) -> Any:
    if name not in TOOL_FUNCTIONS:
        raise ValueError(f"未知工具: {name}")
    result = TOOL_FUNCTIONS[name](**arguments)
    if hasattr(result, "__await__"):
        return await result
    return result
