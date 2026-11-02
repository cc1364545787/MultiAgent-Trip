from __future__ import annotations

import copy
from typing import Any

from app.tools.registry import TOOL_FUNCTIONS


BOUNDS = {
    "days": (1, 14),
    "amount_cny": (1, 1_000_000),
    "budget_cny": (100, 1_000_000),
}

TOOL_REQUIRED = {
    "search_travel": ["query"],
    "get_weather": ["city"],
    "convert_currency": ["amount_cny"],
    "build_calendar": ["days"],
}


class ValidationResult:
    def __init__(self, ok: bool, repaired: dict[str, Any], errors: list[str], auto_fixed: list[str]):
        self.ok = ok
        self.repaired = repaired
        self.errors = errors
        self.auto_fixed = auto_fixed

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": self.errors,
            "auto_fixed": self.auto_fixed,
            "arguments": self.repaired,
        }


def _coerce_number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(",", "").replace("万", "")
        try:
            number = float(cleaned)
            if "万" in value:
                number *= 10000
            return number
        except ValueError:
            return None
    return None


def validate_tool_args(tool: str, arguments: dict[str, Any], context: dict[str, Any] | None = None) -> ValidationResult:
    ctx = context or {}
    args = copy.deepcopy(arguments or {})
    errors: list[str] = []
    fixed: list[str] = []

    if tool not in TOOL_FUNCTIONS:
        return ValidationResult(False, args, [f"非法工具名: {tool}"], fixed)

    required = TOOL_REQUIRED.get(tool, [])
    for key in required:
        if key not in args or args[key] in (None, ""):
            if key == "query" and ctx.get("destination"):
                args["query"] = f"{ctx['destination']} 自由行 攻略"
                fixed.append("补全 search query")
            elif key == "city" and ctx.get("city"):
                args["city"] = ctx["city"]
                fixed.append("补全 city")
            elif key == "amount_cny" and ctx.get("budget_cny"):
                args["amount_cny"] = ctx["budget_cny"]
                fixed.append("补全 amount_cny")
            elif key == "days" and ctx.get("days"):
                args["days"] = ctx["days"]
                fixed.append("补全 days")
            else:
                errors.append(f"缺少必填参数 {key}")

    if "days" in args:
        days = _coerce_number(args["days"])
        if days is None:
            errors.append("days 不是合法数字")
        else:
            lo, hi = BOUNDS["days"]
            clamped = int(max(lo, min(hi, days)))
            if clamped != days:
                fixed.append(f"days {days} 已裁剪到 {clamped}")
            args["days"] = clamped

    if "amount_cny" in args:
        amount = _coerce_number(args["amount_cny"])
        if amount is None:
            errors.append("amount_cny 不是合法数字")
        else:
            lo, hi = BOUNDS["amount_cny"]
            if amount < lo or amount > hi:
                amount = min(hi, max(lo, amount))
                fixed.append("amount_cny 已做边界裁剪")
            args["amount_cny"] = amount

    if tool == "get_weather" and not args.get("city"):
        errors.append("天气查询缺少城市")

    return ValidationResult(ok=len(errors) == 0, repaired=args, errors=errors, auto_fixed=fixed)


def validate_itinerary_payload(payload: dict[str, Any], intent: dict[str, Any]) -> ValidationResult:
    data = copy.deepcopy(payload or {})
    errors: list[str] = []
    fixed: list[str] = []

    days = int(intent.get("days") or data.get("days") or 5)
    data["days"] = days
    data.setdefault("destination", intent.get("destination", ""))
    data.setdefault("budget_cny", intent.get("budget_cny", 0))
    data.setdefault("tips", [])
    data.setdefault("days_plan", [])
    data.setdefault("currency_note", "")
    data.setdefault("weather_summary", "")

    plan = data["days_plan"]
    if len(plan) != days:
        errors.append(f"行程天数 {len(plan)} 与需求 {days} 不一致")

    total = 0
    for i, day in enumerate(plan):
        if "activities" not in day or not day["activities"]:
            errors.append(f"第 {i + 1} 天缺少活动")
        cost = int(day.get("estimated_cost_cny") or 0)
        if cost < 0:
            day["estimated_cost_cny"] = 0
            fixed.append(f"第 {i + 1} 天费用不能为负")
            cost = 0
        total += cost

    data["total_estimated_cny"] = total or int(data.get("total_estimated_cny") or 0)
    budget = int(data.get("budget_cny") or 0)
    data["within_budget"] = data["total_estimated_cny"] <= budget if budget else True
    if budget and data["total_estimated_cny"] > budget * 1.15:
        errors.append("预估花费显著超出预算")

    return ValidationResult(ok=len(errors) == 0, repaired=data, errors=errors, auto_fixed=fixed)
