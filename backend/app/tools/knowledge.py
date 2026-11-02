"""Curated destination knowledge used as a grounded search fallback."""

DESTINATION_GUIDES: dict[str, dict] = {
    "日本": {
        "aliases": ["japan", "东京", "大阪", "京都", "tokyo", "osaka", "kyoto"],
        "cities": ["东京", "京都", "大阪"],
        "highlights": [
            "东京：浅草寺、晴空塔、涩谷十字路口、明治神宫、筑地外围市场",
            "京都：伏见稻荷大社、清水寺、岚山竹林、祗园",
            "大阪：道顿堀、大阪城、心斋桥、环球影城",
        ],
        "food": ["拉面", "寿司", "鳗鱼饭", "大阪烧", "抹茶甜品"],
        "transport": "JR Pass 5 日券适合跨城；市内用 Suica/Pasmo。东京-京都新干线约 2.5 小时。",
        "budget_tips": [
            "商务酒店或胶囊旅馆可把住宿压到 250-450 元/晚",
            "便利店与连锁拉面能有效控制餐饮成本",
            "神社寺庙多数免费或低票价",
        ],
        "sample_route_5d": [
            "D1 东京抵达 + 浅草/晴空塔",
            "D2 涩谷/原宿/明治神宫",
            "D3 新干线赴京都，伏见稻荷 + 祗园",
            "D4 清水寺 + 岚山",
            "D5 大阪道顿堀后返程或从关西机场离开",
        ],
    },
    "韩国": {
        "aliases": ["korea", "首尔", "釜山", "seoul"],
        "cities": ["首尔", "釜山"],
        "highlights": ["景福宫", "明洞", "弘大", "南山塔", "甘川文化村"],
        "food": ["韩式烤肉", "参鸡汤", "拌饭", "街头小吃"],
        "transport": "T-money 交通卡覆盖地铁公交。",
        "budget_tips": ["明洞周边性价比酒店多", "便利店午餐很划算"],
        "sample_route_5d": ["D1-3 首尔皇宫与潮流街区", "D4-5 可选釜山海云台"],
    },
    "泰国": {
        "aliases": ["thailand", "曼谷", "清迈", "普吉", "bangkok"],
        "cities": ["曼谷", "清迈"],
        "highlights": ["大皇宫", "卧佛寺", "恰图恰周末市场", "双条车夜市"],
        "food": ["冬阴功", "芒果糯米饭", "泰式炒河粉"],
        "transport": "曼谷 BTS/MRT + Grab。",
        "budget_tips": ["街边美食极致性价比", "避开景区正餐溢价"],
        "sample_route_5d": ["D1-3 曼谷寺庙与市集", "D4-5 北上清迈或海边"],
    },
}


def match_destination(text: str) -> str:
    lowered = text.lower()
    for name, meta in DESTINATION_GUIDES.items():
        if name in text:
            return name
        if any(alias.lower() in lowered for alias in meta["aliases"]):
            return name
    return "日本" if "玩" in text or "旅行" in text else text.strip()[:20] or "目的地"
