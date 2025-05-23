from __future__ import annotations

from datetime import datetime, timezone, tzinfo

import pytest

from scubaduck import server


class FakeDateTime(datetime):
    @classmethod
    def now(cls, tz: tzinfo | None = None) -> datetime:  # pyright: ignore[override]
        return datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def test_parse_time_absolute() -> None:
    assert server.parse_time("2024-01-02 03:04:05") == "2024-01-02 03:04:05"


def test_parse_time_relative(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server, "datetime", FakeDateTime)
    assert server.parse_time("now") == "2024-01-01 00:00:00"
    assert server.parse_time("2 days") == "2024-01-03 00:00:00"


def test_numeric_to_datetime_and_suggest_unit() -> None:
    expected = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert server._numeric_to_datetime(1704067200, "s") == expected  # pyright: ignore[reportPrivateUsage]
    assert server._numeric_to_datetime(1704067200, "ms") == expected  # pyright: ignore[reportPrivateUsage]
    assert server._suggest_time_unit(1704067200, "ms") == "s"  # pyright: ignore[reportPrivateUsage]


def test_granularity_seconds() -> None:
    assert server._granularity_seconds("1 minute", None, None) == 60  # pyright: ignore[reportPrivateUsage]
    auto = server._granularity_seconds(  # pyright: ignore[reportPrivateUsage]
        "Auto",
        "2024-01-01 00:00:00",
        "2024-01-01 02:00:00",
    )
    assert auto == 72


def test_time_expr_variants() -> None:
    expr_us = server._time_expr("ts", {"ts": "INTEGER"}, "us")  # pyright: ignore[reportPrivateUsage]
    assert expr_us == 'make_timestamp(CAST(CAST("ts" AS BIGINT) * 1000000 AS BIGINT))'
    expr_ns = server._time_expr("ts", {"ts": "BIGINT"}, "ns")  # pyright: ignore[reportPrivateUsage]
    assert expr_ns == 'make_timestamp_ns(CAST("ts" AS BIGINT))'
    expr_ts = server._time_expr("ts", {"ts": "TIMESTAMP"}, "s")  # pyright: ignore[reportPrivateUsage]
    assert expr_ts == '"ts"'
