from __future__ import annotations

import re

import httpx

from app.tools.knowledge import DESTINATION_GUIDES, match_destination


async def search_travel(query: str, destination: str | None = None) -> dict:
    dest = destination or match_destination(query)
    web_snippets: list[str] = []

    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            resp = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            )
            if resp.status_code == 200:
                payload = resp.json()
                abstract = payload.get("AbstractText") or payload.get("Abstract")
                if abstract:
                    web_snippets.append(abstract)
                for topic in payload.get("RelatedTopics", [])[:4]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        web_snippets.append(topic["Text"])
    except Exception:
        pass

    guide = DESTINATION_GUIDES.get(dest) or DESTINATION_GUIDES.get(match_destination(dest))
    grounded = {
        "destination": dest,
        "query": query,
        "web_snippets": web_snippets[:5],
        "highlights": guide["highlights"] if guide else [],
        "food": guide["food"] if guide else [],
        "transport": guide["transport"] if guide else "优先公共交通与步行。",
        "budget_tips": guide["budget_tips"] if guide else ["提前订票、错峰出行。"],
        "sample_route": guide["sample_route_5d"] if guide else [],
        "source": "duckduckgo+curated-knowledge" if web_snippets else "curated-knowledge",
    }
    return grounded


def parse_travel_intent(text: str) -> dict:
    days = 5
    day_match = re.search(r"(\d+)\s*天", text)
    if day_match:
        days = max(1, min(14, int(day_match.group(1))))

    budget = 10000
    budget_match = re.search(r"预算\s*(\d+(?:\.\d+)?)\s*([万wW])?", text)
    if budget_match:
        value = float(budget_match.group(1))
        if budget_match.group(2):
            value *= 10000
        budget = int(value)
    else:
        wan = re.search(r"(\d+(?:\.\d+)?)\s*万", text)
        if wan:
            budget = int(float(wan.group(1)) * 10000)

    destination = match_destination(text)
    return {"destination": destination, "days": days, "budget_cny": budget, "raw": text}
