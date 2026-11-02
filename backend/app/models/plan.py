from typing import Any, Literal

from pydantic import BaseModel, Field


TaskType = Literal["search", "weather", "currency", "calendar"]


class SubTask(BaseModel):
    id: str
    seq: int
    type: TaskType
    title: str
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)


class ToolCallRecord(BaseModel):
    task_id: str
    seq: int
    tool: str
    arguments: dict[str, Any]
    result: Any = None
    ok: bool = True
    error: str | None = None
    retries: int = 0


class Activity(BaseModel):
    time: str
    title: str
    detail: str
    cost_cny: int = 0


class DayPlan(BaseModel):
    day: int
    date: str
    city: str
    theme: str
    weather: str
    activities: list[Activity]
    estimated_cost_cny: int


class Itinerary(BaseModel):
    destination: str
    days: int
    budget_cny: int
    currency_note: str
    weather_summary: str
    days_plan: list[DayPlan]
    tips: list[str]
    total_estimated_cny: int
    within_budget: bool
