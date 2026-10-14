"""Strict bounded JSONL/CSV event adapters; binary evidence is retained opaquely. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: parse — line 34
# parameter: data — line 34
# parameter: format_name — line 34
# variable: text — line 41
# variable: lines — line 44
# variable: line — line 45
# variable: values — line 47
# variable: identifiers — line 48
# variable: line — line 50
# variable: number — line 50
# variable: reader — line 59
# variable: row — line 62
# variable: event — line 74
# END CODE MAP

from __future__ import annotations

import csv
import io

from .contracts import (
    FIELDS,
    MAX_EVENTS,
    MAX_FILE,
    MAX_LINE,
    Event,
    EvidenceError,
    json_value,
)


def parse(data: bytes, format_name: str) -> tuple[Event, ...]:
    """Normalize a bounded complete buffer atomically; duplicate IDs reject the whole import."""
    if format_name not in {"jsonl", "csv", "opaque"} or len(data) > MAX_FILE:
        raise EvidenceError("format_or_size")
    if format_name == "opaque":
        return ()
    try:
        text = data.decode("utf-8")
    except UnicodeError:
        raise EvidenceError("invalid_utf8") from None
    lines = text.splitlines()
    if not lines or any(len(line.encode("utf-8")) > MAX_LINE for line in lines):
        raise EvidenceError("empty_or_oversized_line")
    values: list[Event] = []
    identifiers: set[str] = set()
    if format_name == "jsonl":
        for number, line in enumerate(lines, 1):
            try:
                values.append(Event.parse(json_value(line), number))
            except EvidenceError as error:
                raise EvidenceError(error.code, number) from None
            if len(values) > MAX_EVENTS:
                raise EvidenceError("too_many_events")
    else:
        try:
            reader = csv.reader(io.StringIO(text, newline=""), strict=True)
            if next(reader) != list(FIELDS):
                raise EvidenceError("csv_header")
            for row in reader:
                if len(row) != len(FIELDS):
                    raise EvidenceError("csv_width", reader.line_num)
                values.append(
                    Event.parse(dict(zip(FIELDS, row, strict=True)), reader.line_num)
                )
                if len(values) > MAX_EVENTS:
                    raise EvidenceError("too_many_events")
        except (csv.Error, StopIteration):
            raise EvidenceError("invalid_csv") from None
    if not values:
        raise EvidenceError("empty_events")
    for event in values:
        if event.values[0] in identifiers:
            raise EvidenceError("duplicate_event_id", event.line)
        identifiers.add(event.values[0])
    return tuple(values)
