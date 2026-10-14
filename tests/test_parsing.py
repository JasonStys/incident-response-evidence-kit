"""JSONL/CSV malformed, duplicate, multiline and bounded-input regression tests. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: csv_data — line 41
# parameter: rows — line 41
# variable: stream — line 43
# variable: writer — line 44
# definition: test_json_csv_equivalence — line 50
# variable: original — line 52
# variable: a — line 53
# variable: b — line 54
# definition: test_bad_input — line 75
# parameter: data — line 75
# parameter: format_name — line 75
# definition: test_duplicate_id — line 81
# variable: data — line 83
# definition: test_opaque — line 88
# definition: test_unicode_csv_roundtrip — line 104
# parameter: message — line 104
# variable: original — line 106
# definition: test_event_limit — line 110
# parameter: monkeypatch — line 110
# variable: rows — line 113
# variable: data — line 114
# variable: format_name — line 114
# variable: row — line 116
# END CODE MAP

import csv
import io
import json

import pytest
from conftest import event
from hypothesis import given
from hypothesis import strategies as st

from irkit.contracts import FIELDS, MAX_FILE, EvidenceError
from irkit.parsing import parse


def csv_data(rows):
    """Encode known CSV fixtures with standard quoting; no filesystem or networking."""
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(FIELDS)
    writer.writerows(rows)
    return stream.getvalue().encode()


def test_json_csv_equivalence():
    """Both adapters retain the same normalized fields and original source time."""
    original = event(message='line one\nline two, quoted "detail"')
    a = parse(json.dumps(original).encode(), "jsonl")[0]
    b = parse(csv_data([list(original.values())]), "csv")[0]
    assert a.values == b.values and a.line == 1 and b.line == 3


@pytest.mark.parametrize(
    "data,format_name",
    [
        (b"", "jsonl"),
        (b"", "csv"),
        (b"\xff", "jsonl"),
        (b" ", "jsonl"),
        (b"[]", "jsonl"),
        (b"x,y\na,b", "csv"),
        (csv_data([["x"]]), "csv"),
        (b'event_id,timestamp,kind,actor,asset,message\na,"unterminated', "csv"),
        (b"\n", "csv"),
        (csv_data([]), "csv"),
        (b"x", "unknown"),
        (b"x" * 16385, "jsonl"),
    ],
)
def test_bad_input(data, format_name):
    """All malformed inputs reject atomically rather than discarding bad rows."""
    with pytest.raises(EvidenceError):
        parse(data, format_name)


def test_duplicate_id():
    """Repeated event IDs within one source reject, even when record contents differ."""
    data = (json.dumps(event()) + "\n" + json.dumps(event(kind="alert"))).encode()
    with pytest.raises(EvidenceError, match="duplicate_event_id at record 2"):
        parse(data, "jsonl")


def test_opaque():
    """Binary data stays opaque, including invalid UTF8 and potential archive content."""
    assert parse(b"PK\xff\x00executable-like", "opaque") == ()
    with pytest.raises(EvidenceError):
        parse(b"x" * (MAX_FILE + 1), "opaque")


@given(
    st.text(
        alphabet=st.characters(
            blacklist_categories=("Cs",), blacklist_characters="\x00"
        ),
        min_size=1,
        max_size=40,
    )
)
def test_unicode_csv_roundtrip(message):
    """Quoted commas/newlines/Unicode survive normalization without replacement or omission."""
    original = event(message=message)
    assert parse(csv_data([list(original.values())]), "csv")[0].values[-1] == message


def test_event_limit(monkeypatch):
    """Both adapters enforce the record cap with small disposable data."""
    monkeypatch.setattr("irkit.parsing.MAX_EVENTS", 1)
    rows = [event("a"), event("b")]
    for data, format_name in (
        ("\n".join(map(json.dumps, rows)).encode(), "jsonl"),
        (csv_data([list(row.values()) for row in rows]), "csv"),
    ):
        with pytest.raises(EvidenceError, match="too_many_events"):
            parse(data, format_name)
