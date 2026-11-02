from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator

from langgraph.graph import END, START, StateGraph

from app.graph.nodes import aggregator_node, executor_node, planner_node, route_after_validator, validator_node
from app.graph.state import AgentState
from app.models.events import StreamEvent


def build_graph(emit):
    async def planner(state: AgentState):
        await emit("node_start", "planner", "进入规划者节点", {})
        return await planner_node(state, emit)

    async def executor(state: AgentState):
        await emit("node_start", "executor", "进入执行者节点", {})
        return await executor_node(state, emit)

    async def validator(state: AgentState):
        await emit("node_start", "validator", "进入校验者节点", {})
        return await validator_node(state, emit)

    async def aggregator(state: AgentState):
        await emit("node_start", "aggregator", "进入主控汇总节点", {})
        return await aggregator_node(state, emit)

    graph = StateGraph(AgentState)
    graph.add_node("planner", planner)
    graph.add_node("executor", executor)
    graph.add_node("validator", validator)
    graph.add_node("aggregator", aggregator)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "validator")
    graph.add_conditional_edges("validator", route_after_validator, {"executor": "executor", "aggregator": "aggregator"})
    graph.add_edge("aggregator", END)
    return graph.compile()


async def run_travel_graph(user_input: str) -> AsyncIterator[StreamEvent]:
    queue: asyncio.Queue[StreamEvent | None] = asyncio.Queue()

    async def emit(event_type: str, node: str, message: str, data: dict[str, Any]) -> None:
        await queue.put(StreamEvent(type=event_type, node=node, message=message, data=data))  # type: ignore[arg-type]

    graph = build_graph(emit)

    async def runner() -> None:
        try:
            await emit("run_started", "graph", "多 Agent 工作流已启动", {"user_input": user_input})
            initial: AgentState = {
                "user_input": user_input,
                "intent": {},
                "plan": [],
                "messages": [],
                "tool_results": {},
                "records": [],
                "validation_errors": [],
                "retry_count": 0,
                "itinerary": None,
                "status": "planning",
                "traces": [],
            }
            await graph.ainvoke(initial)
            await emit("done", "graph", "工作流结束", {"status": "done"})
        except Exception as exc:  # noqa: BLE001
            await emit("error", "graph", str(exc), {"status": "failed"})
        finally:
            await queue.put(None)

    task = asyncio.create_task(runner())
    try:
        while True:
            event = await queue.get()
            if event is None:
                break
            yield event
    finally:
        await task
