"""Tests for helper time functions in :mod:`scubaduck.server`."""

# pyright: reportPrivateUsage=false

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

import pytest

from scubaduck.server import (
    _numeric_to_datetime,
    _suggest_time_unit,
    parse_time,
)


def test_parse_time_now_has_expected_format() -> None:
    """``parse_time('now')`` returns a ``YYYY-MM-DD HH:MM:SS`` string."""

    value = parse_time("now")
    assert value is not None
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", value)


def test_parse_time_relative_day() -> None:
    """Relative time strings are offset from the current time."""

    value = parse_time("1 day")
    assert value is not None
    dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    now = datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)
    delta = dt - now
    assert timedelta(hours=20) < delta < timedelta(hours=28)


@pytest.mark.parametrize(
    "value,unit,expected_year",
    [
        (631_152_000, "ms", 1990),
        (1_704_067_200_000, "ms", 2023),
    ],
)
def test_numeric_to_datetime(value: int, unit: str, expected_year: int) -> None:
    """Numeric timestamps are converted to reasonable datetimes."""

    dt = _numeric_to_datetime(value, unit)
    assert dt.year >= expected_year


def test_suggest_time_unit_finds_reasonable_unit() -> None:
    """Suggest ``ms`` when ``us`` gives an implausible year."""

    value = 1_704_067_200_000
    assert _suggest_time_unit(value, "us") == "ms"
    assert _suggest_time_unit(value, "ms") is None
