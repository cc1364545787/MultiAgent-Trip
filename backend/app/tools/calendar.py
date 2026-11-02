from __future__ import annotations

from datetime import date, timedelta


WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def build_calendar(days: int = 5, start_date: str | None = None) -> dict:
    days = max(1, min(14, int(days)))
    start = date.fromisoformat(start_date) if start_date else date.today() + timedelta(days=7)
    items = []
    for i in range(days):
        current = start + timedelta(days=i)
        items.append(
            {
                "day": i + 1,
                "date": current.isoformat(),
                "weekday": WEEKDAYS[current.weekday()],
            }
        )
    return {
        "start_date": start.isoformat(),
        "end_date": items[-1]["date"],
        "days": days,
        "dates": items,
    }
