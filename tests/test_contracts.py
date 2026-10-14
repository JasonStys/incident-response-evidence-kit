"""UTC/schema/JSON/property validation with independent expected values. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_utc — line 43
# parameter: expected — line 43
# parameter: source — line 43
# definition: test_bad_time — line 67
# parameter: source — line 67
# definition: test_fraction_property — line 74
# parameter: fraction — line 74
# variable: value — line 76
# definition: test_bad_operator — line 83
# parameter: value — line 83
# definition: test_good_operator — line 89
# definition: test_json_errors — line 97
# parameter: data — line 97
# variable: error — line 99
# definition: test_canonical_hash — line 104
# definition: test_event_rejected — line 131
# parameter: value — line 131
# definition: test_event_private_repr — line 137
# variable: parsed — line 139
# END CODE MAP

import json

import pytest
from conftest import event
from hypothesis import given
from hypothesis import strategies as st

from irkit.contracts import Event, EvidenceError, canonical, json_value, sha, token, utc


@pytest.mark.parametrize(
    "source,expected",
    [
        ("2026-10-10T09:00:00-07:00", "2026-10-10T16:00:00.000000Z"),
        ("2026-10-10T18:00:00+02:00", "2026-10-10T16:00:00.000000Z"),
        ("2026-10-10T16:00:00.123456Z", "2026-10-10T16:00:00.123456Z"),
        ("2026-01-01T00:00:00+14:00", "2025-12-31T10:00:00.000000Z"),
    ],
)
def test_utc(source, expected):
    """Equivalent offsets normalize exactly, including fractions and previous-day rollover."""
    assert utc(source) == expected


@pytest.mark.parametrize(
    "source",
    [
        None,
        42,
        "",
        "2026-11-01T01:30:00",
        "2026-10-10 16:00:00Z",
        "2026-10-10T16:00:00-00:00",
        "2026-10-10T16:00:00+14:01",
        "2026-10-10T16:00:60Z",
        "2026-02-30T16:00:00Z",
        "2026-10-10T16:00:00.1234567Z",
        "1999-12-31T23:59:59Z",
        "2101-01-01T00:00:00Z",
        "2000-01-01T00:00:00+01:00",
        "2026-10-10T16:00:00+99:00",
    ],
)
def test_bad_time(source):
    """Naive/DST-ambiguous, unknown offset, leap second, malformed and out-of-range values fail."""
    with pytest.raises(EvidenceError):
        utc(source)


@given(st.integers(0, 999999))
def test_fraction_property(fraction):
    """Fixed-width UTC preserves every valid microsecond and lexicographic chronological ordering."""
    value = f"2026-10-10T16:00:00.{fraction:06}Z"
    assert utc(value) == value


@pytest.mark.parametrize(
    "value", ["", "../escape", "Alice Smith", "=formula", "a" * 49, 1, None]
)
def test_bad_operator(value):
    """Operator references cannot become paths, arbitrary display strings or formula expressions."""
    with pytest.raises(EvidenceError):
        token(value)


def test_good_operator():
    """Bounded nonidentifying slug is retained without hidden case conversion."""
    assert token("analyst-a_2") == "analyst-a_2"


@pytest.mark.parametrize(
    "data", [b"\xff", "{", '{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}', "[" * 1200]
)
def test_json_errors(data):
    """Unsafe JSON cannot silently discard duplicates or publish raw parser snippets."""
    with pytest.raises(EvidenceError) as error:
        json_value(data)
    assert "PRIVATE" not in str(error.value)


def test_canonical_hash():
    """Canonical key order is stable; fixed SHA256 abc vector independently validates digest."""
    assert canonical({"b": 2, "a": 1}) == b'{"a":1,"b":2}'
    assert (
        sha(b"abc")
        == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )
    with pytest.raises(ValueError):
        canonical(float("nan"))


@pytest.mark.parametrize(
    "value",
    [
        [],
        {},
        event(extra="not-allowed"),
        event(actor=""),
        event(message="x" * 4097),
        event(actor="x" * 257),
        event(actor=None),
        event(asset="a\x00b"),
        event(kind="arbitrary raw text"),
        event(timestamp="naive"),
        event(actor="\ud800"),
    ],
)
def test_event_rejected(value):
    """Strict complete schema prevents silently dropped data and free-form exported event kinds."""
    with pytest.raises(EvidenceError):
        Event.parse(value, 3)


def test_event_private_repr():
    """Identifiers/content are omitted from dataclass repr but retained in private commitment."""
    parsed = Event.parse(event(), 3)
    assert "PRIVATE" not in repr(parsed) and "person" not in repr(parsed)
    assert parsed.committed()[0] == 3 and "PRIVATE" in json.dumps(parsed.committed())
