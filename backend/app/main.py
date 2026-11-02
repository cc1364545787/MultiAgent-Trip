from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.graph.workflow import run_travel_graph

app = FastAPI(title="Multi-Agent Travel Planner", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlanRequest(BaseModel):
    query: str = Field(..., min_length=2, examples=["我想去日本玩 5 天，预算 1 万"])


@app.get("/api/health")
async def health():
    return {"ok": True, "llm": settings.llm_enabled, "model": settings.openai_model if settings.llm_enabled else "rule-based"}


@app.post("/api/plan/stream")
async def plan_stream(body: PlanRequest):
    async def event_source():
        async for event in run_travel_graph(body.query.strip()):
            yield f"data: {event.model_dump_json()}\n\n"
        yield "data: {\"type\":\"close\"}\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/plan")
async def plan_once(body: PlanRequest):
    events = []
    itinerary = None
    async for event in run_travel_graph(body.query.strip()):
        events.append(event.model_dump())
        if event.type == "itinerary":
            itinerary = event.data.get("itinerary")
    return {"itinerary": itinerary, "events": events, "llm": settings.llm_enabled}
