from __future__ import annotations

from datetime import datetime, timezone

import pytest

from scubaduck import server


class FixedDateTime(datetime):
    """Helper datetime class with overridable ``now``."""

    fixed_now = datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)

    @classmethod
    def now(cls, tz=None):  # type: ignore[override]
        if tz is None:
            return cls.fixed_now
        return cls.fixed_now.astimezone(tz)


def test_parse_time_relative(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server, "datetime", FixedDateTime)
    assert server.parse_time("-1 day") == "2024-01-01 12:00:00"
    assert server.parse_time("now") == "2024-01-02 12:00:00"


def test_numeric_to_datetime_ms() -> None:
    dt = server._numeric_to_datetime(1704067200000, "ms")  # pyright: ignore[reportPrivateUsage]
    assert dt == datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)


def test_numeric_to_datetime_fallback() -> None:
    dt = server._numeric_to_datetime(1704067200, "ms")  # pyright: ignore[reportPrivateUsage]
    assert dt == datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)


def test_suggest_time_unit() -> None:
    assert server._suggest_time_unit(1704067200000, "s") == "ms"  # pyright: ignore[reportPrivateUsage]
    assert server._suggest_time_unit(1, "s") is None  # pyright: ignore[reportPrivateUsage]


def test_granularity_seconds_auto_fine() -> None:
    start = "2024-01-01 00:00:00"
    end = "2024-01-02 00:00:00"
    assert server._granularity_seconds("Auto", start, end) == 864  # pyright: ignore[reportPrivateUsage]
    assert server._granularity_seconds("Fine", start, end) == 172  # pyright: ignore[reportPrivateUsage]
    assert server._granularity_seconds("unknown", None, None) == 3600  # pyright: ignore[reportPrivateUsage]
