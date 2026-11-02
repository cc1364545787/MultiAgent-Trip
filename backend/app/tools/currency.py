from __future__ import annotations

import httpx

DEST_CURRENCY = {
    "日本": "JPY",
    "韩国": "KRW",
    "泰国": "THB",
    "美国": "USD",
    "英国": "GBP",
    "法国": "EUR",
    "意大利": "EUR",
}


async def convert_currency(amount_cny: float, target_currency: str = "JPY", destination: str | None = None) -> dict:
    amount = max(0.0, float(amount_cny))
    currency = (target_currency or "JPY").upper()
    if destination and destination in DEST_CURRENCY:
        currency = DEST_CURRENCY[destination]

    rate = None
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(
                "https://api.frankfurter.app/latest",
                params={"from": "CNY", "to": currency},
            )
            resp.raise_for_status()
            rate = float(resp.json()["rates"][currency])
            source = "frankfurter"
    except Exception:
        fallback = {"JPY": 21.0, "KRW": 190.0, "THB": 4.6, "USD": 0.14, "EUR": 0.13, "GBP": 0.11}
        rate = fallback.get(currency, 1.0)
        source = "fallback-rate"

    converted = round(amount * rate, 2)
    return {
        "amount_cny": amount,
        "target_currency": currency,
        "rate": rate,
        "converted": converted,
        "note": f"1 CNY ≈ {rate:.4f} {currency}，预算 {amount:.0f} 元约合 {converted:.0f} {currency}",
        "source": source,
    }
