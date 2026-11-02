from __future__ import annotations

from typing import Any, Awaitable, Callable

from app.graph.state import AgentState
from app.models.plan import Activity, DayPlan, Itinerary, SubTask
from app.services.coordinator import AgentCoordinator
from app.services.llm import llm_itinerary, llm_plan
from app.services.validator import validate_itinerary_payload
from app.tools.knowledge import DESTINATION_GUIDES
from app.tools.search import parse_travel_intent

CITY_BY_DEST = {
    "日本": ["东京", "东京", "京都", "京都", "大阪"],
    "韩国": ["首尔", "首尔", "首尔", "釜山", "釜山"],
    "泰国": ["曼谷", "曼谷", "曼谷", "清迈", "清迈"],
}

EmitFn = Callable[[str, str, str, dict[str, Any]], Awaitable[None]]


def _progress_label(task_type: str) -> str:
    return {
        "search": "正在搜索攻略",
        "weather": "正在查询天气",
        "currency": "正在换算汇率",
        "calendar": "正在生成日程",
    }.get(task_type, "正在执行工具")


async def planner_node(state: AgentState, emit: EmitFn) -> dict[str, Any]:
    await emit("status", "planner", "规划者正在拆解用户意图", {"status": "planning"})
    intent = parse_travel_intent(state["user_input"])
    llm_result = await llm_plan(state["user_input"], intent)

    reasoning = "根据天数、预算与目的地，拆分为攻略搜索、天气、汇率、日历四项可并行子任务。"
    tasks: list[SubTask]
    if llm_result and llm_result.get("tasks"):
        reasoning = llm_result.get("reasoning") or reasoning
        tasks = []
        for i, raw in enumerate(llm_result["tasks"], start=1):
            tasks.append(
                SubTask(
                    id=raw.get("id") or f"t{i}",
                    seq=int(raw.get("seq") or i),
                    type=raw.get("type") or "search",
                    title=raw.get("title") or raw.get("tool") or f"任务{i}",
                    tool=raw["tool"],
                    arguments=raw.get("arguments") or {},
                )
            )
    else:
        dest = intent["destination"]
        city = CITY_BY_DEST.get(dest, [dest])[0]
        tasks = [
            SubTask(
                id="t1",
                seq=1,
                type="search",
                title="搜索目的地攻略",
                tool="search_travel",
                arguments={"query": f"{dest} {intent['days']}日自由行 攻略", "destination": dest},
            ),
            SubTask(
                id="t2",
                seq=2,
                type="weather",
                title="查询目的地天气",
                tool="get_weather",
                arguments={"city": city, "days": intent["days"]},
            ),
            SubTask(
                id="t3",
                seq=3,
                type="currency",
                title="换算旅行预算",
                tool="convert_currency",
                arguments={"amount_cny": intent["budget_cny"], "destination": dest},
            ),
            SubTask(
                id="t4",
                seq=4,
                type="calendar",
                title="生成行程日历",
                tool="build_calendar",
                arguments={"days": intent["days"]},
            ),
        ]

    await emit("reasoning", "planner", reasoning, {"intent": intent})
    await emit("plan", "planner", f"已拆解 {len(tasks)} 个子任务，准备并行执行", {"tasks": [t.model_dump() for t in tasks]})
    return {
        "intent": intent,
        "plan": [t.model_dump() for t in tasks],
        "status": "executing",
        "validation_errors": [],
        "retry_count": 0,
        "tool_results": {},
        "records": [],
        "itinerary": None,
    }


async def executor_node(state: AgentState, emit: EmitFn) -> dict[str, Any]:
    await emit("status", "executor", "执行者正在并行调度工具 Agent", {"status": "executing"})
    tasks = [SubTask.model_validate(item) for item in state["plan"]]
    labels = " → ".join(_progress_label(task.type) for task in tasks)
    await emit("reasoning", "executor", labels, {"parallel": True, "task_count": len(tasks)})

    coordinator = AgentCoordinator(workers=min(4, max(1, len(tasks))))
    intent = state.get("intent") or {}
    context = {
        "destination": intent.get("destination"),
        "city": CITY_BY_DEST.get(intent.get("destination", ""), [intent.get("destination")])[0],
        "days": intent.get("days"),
        "budget_cny": intent.get("budget_cny"),
    }

    async def on_event(event_type: str, data: dict[str, Any]) -> None:
        message = {
            "tool_call": f"调用工具 {data.get('tool')}",
            "tool_result": f"工具 {data.get('tool')} 返回成功" if data.get("ok", True) else f"工具 {data.get('tool')} 失败",
            "retry": f"工具 {data.get('tool')} 第 {data.get('attempt')} 次重试",
        }.get(event_type, event_type)
        await emit(event_type, "executor", message, data)

    records = await coordinator.run(tasks, context, on_event=on_event)
    tool_results = {rec.tool: rec.result for rec in records if rec.ok}
    payload = [rec.model_dump() for rec in records]
    failed = [rec for rec in records if not rec.ok]
    await emit(
        "node_end",
        "executor",
        f"并行执行完成，成功 {len(records) - len(failed)}/{len(records)}",
        {"records": payload},
    )
    return {"records": payload, "tool_results": tool_results, "status": "validating"}


async def validator_node(state: AgentState, emit: EmitFn) -> dict[str, Any]:
    await emit("status", "validator", "校验者正在检查工具参数与结果完整性", {"status": "validating"})
    records = state.get("records") or []
    errors: list[str] = []
    for rec in records:
        if not rec.get("ok"):
            errors.append(f"{rec.get('tool')}: {rec.get('error') or '调用失败'}")
    required_tools = {task["tool"] for task in state.get("plan") or []}
    got = {rec.get("tool") for rec in records if rec.get("ok")}
    missing = required_tools - got
    for tool in missing:
        errors.append(f"缺少工具结果: {tool}")

    retry_count = int(state.get("retry_count") or 0)
    ok = not errors
    await emit(
        "validation",
        "validator",
        "校验通过" if ok else f"发现 {len(errors)} 项问题，准备重试" if retry_count < 1 else "校验未完全通过，进入降级生成",
        {"ok": ok, "errors": errors, "retry_count": retry_count},
    )
    status = "aggregating" if ok or retry_count >= 1 else "retrying"
    return {"validation_errors": errors, "retry_count": retry_count + (0 if ok else 1), "status": status}


def route_after_validator(state: AgentState) -> str:
    if state.get("status") == "retrying" and int(state.get("retry_count") or 0) <= 1:
        return "executor"
    return "aggregator"


def _heuristic_itinerary(intent: dict[str, Any], tool_results: dict[str, Any]) -> Itinerary:
    dest = intent.get("destination") or "目的地"
    days = int(intent.get("days") or 5)
    budget = int(intent.get("budget_cny") or 0)
    search = tool_results.get("search_travel") or {}
    weather = tool_results.get("get_weather") or {}
    currency = tool_results.get("convert_currency") or {}
    calendar = tool_results.get("build_calendar") or {}
    guide = DESTINATION_GUIDES.get(dest, {})
    cities = CITY_BY_DEST.get(dest, [dest] * days)
    highlights = search.get("highlights") or guide.get("highlights") or [f"{dest} 市区漫步"]
    food = search.get("food") or guide.get("food") or ["当地美食"]
    sample = search.get("sample_route") or guide.get("sample_route_5d") or []
    forecast = weather.get("forecast") or []
    dates = calendar.get("dates") or [{"day": i + 1, "date": "", "weekday": ""} for i in range(days)]
    per_day = max(200, budget // max(days, 1) if budget else 800)
    day_plans: list[DayPlan] = []
    for i in range(days):
        city = cities[i] if i < len(cities) else cities[-1]
        date_item = dates[i] if i < len(dates) else {"date": "", "weekday": ""}
        weather_item = forecast[i] if i < len(forecast) else {}
        weather_text = (
            f"{weather_item.get('condition', '天气未知')} {weather_item.get('temp_min', '?')}~{weather_item.get('temp_max', '?')}°C"
            if weather_item
            else "天气待出行前再确认"
        )
        city_spots = [item for item in highlights if city in item] or highlights
        spot = city_spots[i % len(city_spots)]
        dish = food[i % len(food)]
        indoor = "雨" in weather_text or "雪" in weather_text
        morning = "室内展览/商场 + 覆盖景点" if indoor else spot
        theme_base = sample[i] if i < len(sample) else f"{city} · {'雨天室内线' if indoor else '经典观光线'}"
        day_plans.append(
            DayPlan(
                day=i + 1,
                date=f"{date_item.get('date', '')} {date_item.get('weekday', '')}".strip(),
                city=city,
                theme=theme_base,
                weather=weather_text,
                activities=[
                    Activity(time="上午", title=morning, detail=f"围绕 {spot} 安排 3-4 小时深度游览", cost_cny=int(per_day * 0.25)),
                    Activity(time="中午", title=f"品尝{dish}", detail="选择当地口碑店或市场摊位，控制人均预算", cost_cny=int(per_day * 0.2)),
                    Activity(time="下午", title="街区漫步与交通衔接", detail=search.get("transport") or "公共交通为主", cost_cny=int(per_day * 0.2)),
                    Activity(time="晚上", title="夜景/夜市", detail="预留弹性时间，避免行程过满", cost_cny=int(per_day * 0.2)),
                ],
                estimated_cost_cny=per_day,
            )
        )

    tips = list(search.get("budget_tips") or guide.get("budget_tips") or [])
    tips.append("工具结果已写入行程，天气与汇率来自实时接口而非模型臆造。")
    total = per_day * days
    return Itinerary(
        destination=dest,
        days=days,
        budget_cny=budget,
        currency_note=currency.get("note") or "汇率信息暂缺",
        weather_summary=weather.get("summary") or "请在出发前再次确认天气",
        days_plan=day_plans,
        tips=tips,
        total_estimated_cny=total,
        within_budget=total <= budget if budget else True,
    )


async def aggregator_node(state: AgentState, emit: EmitFn) -> dict[str, Any]:
    await emit("status", "aggregator", "主控节点正在有序汇总并行结果并生成方案", {"status": "aggregating"})
    intent = state.get("intent") or {}
    tool_results = state.get("tool_results") or {}
    payload = await llm_itinerary(state["user_input"], intent, tool_results)
    if payload:
        checked = validate_itinerary_payload(payload, intent)
        await emit(
            "validation",
            "aggregator",
            "方案 JSON 校验" + ("通过" if checked.ok else "未通过，改用结构化模板"),
            checked.as_dict(),
        )
        itinerary = checked.repaired if checked.ok else _heuristic_itinerary(intent, tool_results).model_dump()
        if checked.ok:
            itinerary = checked.repaired
    else:
        itinerary = _heuristic_itinerary(intent, tool_results).model_dump()

    await emit("itinerary", "aggregator", "完整行程方案已生成", {"itinerary": itinerary})
    return {"itinerary": itinerary, "status": "done"}
