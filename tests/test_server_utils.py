"""Additional tests for server utility functions."""

# pyright: reportPrivateUsage=false

from scubaduck import server


def test_quote():
    """Identifiers should be SQL quoted and double quotes escaped."""

    assert server._quote("simple") == '"simple"'
    assert server._quote('a"b') == '"a""b"'


def test_numeric_to_datetime_fallback():
    """Ensure heuristic fallback converts large values correctly."""

    ts = 1609459200  # 2021-01-01 in seconds
    dt = server._numeric_to_datetime(ts, "ms")
    assert dt.year == 2021


def test_suggest_time_unit():
    """Suggest a sensible time unit when given one is wrong."""

    ts = 1609459200  # 2021-01-01 in seconds
    assert server._suggest_time_unit(ts, "ms") == "s"


def test_granularity_seconds():
    """Granularity mappings and auto calculation should work."""

    assert server._granularity_seconds("1 hour", None, None) == 3600
    auto = server._granularity_seconds(
        "auto", "2024-01-01 00:00:00", "2024-01-02 00:00:00"
    )
    assert auto == 864
    assert server._granularity_seconds("unknown", None, None) == 3600


def test_time_expr_numeric():
    """Numeric columns should be converted to timestamps depending on unit."""

    cols = {"ts32": "INT", "ts64": "BIGINT", "ts": "TIMESTAMP"}
    expr32 = server._time_expr("ts32", cols, "ms")
    expr64 = server._time_expr("ts64", cols, "ms")
    expr_ts = server._time_expr("ts", cols, "ms")
    assert expr32 == 'make_timestamp(CAST(CAST("ts32" AS BIGINT) * 1000000 AS BIGINT))'
    assert expr64 == 'make_timestamp(CAST(CAST("ts64" AS BIGINT) * 1000 AS BIGINT))'
    assert expr_ts == '"ts"'
