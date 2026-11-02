from __future__ import annotations

import httpx

CITY_FALLBACKS = {
    "东京": (35.6762, 139.6503),
    "京都": (35.0116, 135.7681),
    "大阪": (34.6937, 135.5023),
    "首尔": (37.5665, 126.9780),
    "曼谷": (13.7563, 100.5018),
    "日本": (35.6762, 139.6503),
}

WEATHER_CODES = {
    0: "晴",
    1: "大部晴朗",
    2: "多云",
    3: "阴",
    45: "雾",
    51: "小雨",
    61: "雨",
    71: "雪",
    80: "阵雨",
    95: "雷阵雨",
}


async def _geocode(city: str) -> tuple[float, float, str]:
    if city in CITY_FALLBACKS:
        lat, lon = CITY_FALLBACKS[city]
        return lat, lon, city
    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "zh"},
        )
        resp.raise_for_status()
        results = resp.json().get("results") or []
        if not results:
            lat, lon = CITY_FALLBACKS.get("东京", (35.67, 139.65))
            return lat, lon, city
        item = results[0]
        return item["latitude"], item["longitude"], item.get("name", city)


async def get_weather(city: str, days: int = 5) -> dict:
    days = max(1, min(14, int(days)))
    lat, lon, resolved = await _geocode(city)
    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "forecast_days": days,
                "timezone": "auto",
            },
        )
        resp.raise_for_status()
        daily = resp.json().get("daily", {})

    forecast = []
    dates = daily.get("time", [])
    for i, date in enumerate(dates):
        code = int((daily.get("weathercode") or [0])[i] if i < len(daily.get("weathercode") or []) else 0)
        forecast.append(
            {
                "date": date,
                "condition": WEATHER_CODES.get(code, "多云"),
                "temp_max": (daily.get("temperature_2m_max") or [None])[i],
                "temp_min": (daily.get("temperature_2m_min") or [None])[i],
                "rain_prob": (daily.get("precipitation_probability_max") or [None])[i],
            }
        )

    summary = "、".join(f"{item['date']} {item['condition']} {item['temp_min']}~{item['temp_max']}°C" for item in forecast[:3])
    return {
        "city": resolved,
        "days": days,
        "forecast": forecast,
        "summary": summary or f"{resolved} 近期天气数据暂缺，建议随身带折叠伞。",
        "source": "open-meteo",
    }
