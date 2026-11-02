from app.services.validator import validate_tool_args


def test_repairs_missing_amount():
    result = validate_tool_args("convert_currency", {}, {"budget_cny": 10000})
    assert result.ok
    assert result.repaired["amount_cny"] == 10000
    assert result.auto_fixed


def test_clamps_days():
    result = validate_tool_args("build_calendar", {"days": 99})
    assert result.ok
    assert result.repaired["days"] == 14
