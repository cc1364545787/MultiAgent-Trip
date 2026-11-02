from __future__ import annotations

import json
from typing import Any

from app.config import settings


def get_chat_model():
    if not settings.llm_enabled:
        return None
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_model,
        temperature=0.3,
    )


async def llm_json(system: str, user: str, schema_hint: str = "") -> dict[str, Any] | None:
    model = get_chat_model()
    if model is None:
        return None
    prompt = user
    if schema_hint:
        prompt += f"\n\n只返回 JSON，不要 Markdown。Schema: {schema_hint}"
    response = await model.ainvoke(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
    )
    text = response.content if isinstance(response.content, str) else str(response.content)
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


async def llm_plan(user_input: str, intent: dict) -> dict | None:
    return await llm_json(
        system="你是旅行规划者 Agent。把用户需求拆成可并行的工具任务。",
        user=f"用户输入: {user_input}\n已解析意图: {json.dumps(intent, ensure_ascii=False)}",
        schema_hint='{"reasoning":"string","tasks":[{"id":"t1","seq":1,"type":"search|weather|currency|calendar","title":"string","tool":"search_travel|get_weather|convert_currency|build_calendar","arguments":{}}]}',
    )


async def llm_itinerary(user_input: str, intent: dict, tool_results: dict) -> dict | None:
    return await llm_json(
        system="你是行程撰写 Agent。必须基于工具返回的真实数据生成行程，禁止编造天气数字与汇率。",
        user=(
            f"用户: {user_input}\n意图: {json.dumps(intent, ensure_ascii=False)}\n"
            f"工具结果: {json.dumps(tool_results, ensure_ascii=False)[:8000]}"
        ),
        schema_hint=(
            '{"destination":"","days":5,"budget_cny":0,"currency_note":"","weather_summary":"",'
            '"days_plan":[{"day":1,"date":"YYYY-MM-DD","city":"","theme":"","weather":"",'
            '"activities":[{"time":"上午","title":"","detail":"","cost_cny":0}],"estimated_cost_cny":0}],'
            '"tips":[],"total_estimated_cny":0,"within_budget":true}'
        ),
    )
