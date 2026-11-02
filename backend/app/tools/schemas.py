TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_travel",
            "description": "搜索目的地攻略、景点、交通与美食信息。用户提到旅行/攻略时必须调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索词，例如「日本 5 日自由行 攻略」"},
                    "destination": {"type": "string", "description": "规范化目的地名称，如 日本/东京"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询城市未来若干天天气预报，用于安排室内/室外行程。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名，如 东京"},
                    "days": {"type": "integer", "description": "预报天数 1-14", "minimum": 1, "maximum": 14},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "将人民币预算换算为目的地货币。",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount_cny": {"type": "number", "description": "人民币金额"},
                    "target_currency": {"type": "string", "description": "目标货币代码，如 JPY"},
                    "destination": {"type": "string", "description": "目的地，用于推断货币"},
                },
                "required": ["amount_cny"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_calendar",
            "description": "生成行程日期表，包含星期。",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "minimum": 1, "maximum": 14},
                    "start_date": {"type": "string", "description": "YYYY-MM-DD，缺省则从一周后开始"},
                },
                "required": ["days"],
            },
        },
    },
]
