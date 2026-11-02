from app.tools.search import parse_travel_intent


def test_parse_japan_five_days():
    intent = parse_travel_intent("我想去日本玩 5 天，预算 1 万")
    assert intent["destination"] == "日本"
    assert intent["days"] == 5
    assert intent["budget_cny"] == 10000
