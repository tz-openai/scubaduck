from datetime import datetime, timezone

import pytest

from scubaduck import server


def test_parse_time_now(monkeypatch: pytest.MonkeyPatch) -> None:
    fixed = datetime(2024, 1, 1, 12, 34, 56, tzinfo=timezone.utc)

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            return fixed if tz is None else fixed.astimezone(tz)

    monkeypatch.setattr(server, "datetime", FixedDateTime)
    assert server.parse_time("now") == "2024-01-01 12:34:56"


def test_parse_time_relative(monkeypatch: pytest.MonkeyPatch) -> None:
    fixed = datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc)

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            return fixed if tz is None else fixed.astimezone(tz)

    monkeypatch.setattr(server, "datetime", FixedDateTime)
    assert server.parse_time("-1 day") == "2024-01-01 00:00:00"
    assert server.parse_time("+2 hours") == "2024-01-02 02:00:00"


def test_numeric_to_datetime_ms_fallback() -> None:
    ts_seconds = 1704067200  # 2024-01-01 00:00:00 UTC
    dt = server._numeric_to_datetime(ts_seconds, "ms")  # pyright: ignore[reportPrivateUsage]
    assert dt == datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)


def test_suggest_time_unit() -> None:
    assert server._suggest_time_unit(1704067200, "ms") == "s"  # pyright: ignore[reportPrivateUsage]
    assert server._suggest_time_unit(1704067200000, "ms") is None  # pyright: ignore[reportPrivateUsage]


def test_granularity_seconds_mapping() -> None:
    assert server._granularity_seconds("1 minute", None, None) == 60  # pyright: ignore[reportPrivateUsage]


def test_granularity_seconds_auto() -> None:
    start = "2024-01-01 00:00:00"
    end = "2024-01-01 01:00:00"
    assert server._granularity_seconds("auto", start, end) == 36  # pyright: ignore[reportPrivateUsage]
    assert server._granularity_seconds("fine", start, end) == 7  # pyright: ignore[reportPrivateUsage]
    assert server._granularity_seconds("auto", "bad", end) == 3600  # pyright: ignore[reportPrivateUsage]
