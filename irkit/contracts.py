"""Strict schemas, safe errors and microsecond UTC normalization. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: MAX_FILE — line 62
# variable: MAX_CASE — line 63
# variable: MAX_EVENTS — line 64
# variable: MAX_CUSTODY — line 65
# variable: MAX_LINE — line 66
# variable: KINDS — line 67
# variable: FIELDS — line 78
# variable: STAMP — line 79
# variable: TOKEN — line 82
# variable: DIGEST — line 83
# definition: EvidenceError — line 86
# definition: __init__ — line 89
# parameter: code — line 89
# parameter: line — line 89
# parameter: self — line 89
# attribute: code — line 91
# attribute: line — line 92
# definition: canonical — line 96
# parameter: value — line 96
# definition: sha — line 103
# parameter: value — line 103
# definition: token — line 108
# parameter: value — line 108
# definition: utc — line 115
# parameter: value — line 115
# variable: parsed — line 124
# variable: offset — line 125
# variable: normalized — line 128
# definition: unique_object — line 136
# parameter: pairs — line 136
# variable: result — line 138
# variable: key — line 139
# variable: value — line 139
# definition: reject_constant — line 146
# parameter: value — line 146
# definition: json_value — line 151
# parameter: data — line 151
# definition: Event — line 162
# variable: line — line 165
# variable: values — line 166
# definition: parse — line 169
# parameter: cls — line 169
# parameter: line — line 169
# parameter: value — line 169
# variable: name — line 178
# variable: name — line 184
# definition: committed — line 201
# parameter: self — line 201
# END CODE MAP

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

MAX_FILE = 20 * 1024 * 1024
MAX_CASE = 64 * 1024 * 1024
MAX_EVENTS = 50_000
MAX_CUSTODY = 10_000
MAX_LINE = 16_384
KINDS = frozenset(
    {
        "auth_failure",
        "auth_success",
        "process_start",
        "connection",
        "blocked",
        "configuration",
        "alert",
    }
)
FIELDS = ("event_id", "timestamp", "kind", "actor", "asset", "message")
STAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})\Z"
)
TOKEN = re.compile(r"[a-z][a-z0-9_-]{0,47}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")


class EvidenceError(ValueError):
    """Expose only a fixed error code/optional record number, never untrusted content."""

    def __init__(self, code: str, line: int = 0) -> None:
        """Set code and line; callers use constant codes without raw input or filenames."""
        self.code = code
        self.line = line
        super().__init__(f"{code}" + (f" at record {line}" if line else ""))


def canonical(value: object) -> bytes:
    """Encode a JSON-compatible value deterministically; NaN/Infinity are forbidden."""
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("ascii")


def sha(value: bytes) -> str:
    """Return lowercase SHA256 using the platform library; do not invent cryptography."""
    return hashlib.sha256(value).hexdigest()


def token(value: object) -> str:
    """Validate a bounded operator code, not a path, person name or arbitrary display label."""
    if not isinstance(value, str) or not TOKEN.fullmatch(value):
        raise EvidenceError("invalid_operator_code")
    return value


def utc(value: object) -> str:
    """Normalize explicit offset timestamps to fixed-width UTC; never infer DST/local time."""
    if (
        not isinstance(value, str)
        or not STAMP.fullmatch(value)
        or value.endswith("-00:00")
    ):
        raise EvidenceError("timestamp_requires_known_offset")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        offset = parsed.utcoffset()
        if offset is None or abs(offset.total_seconds()) > 14 * 3600:
            raise ValueError
        normalized = parsed.astimezone(UTC)
        if not 2000 <= normalized.year <= 2100:
            raise ValueError
        return normalized.isoformat(timespec="microseconds").replace("+00:00", "Z")
    except (ValueError, OverflowError):
        raise EvidenceError("invalid_timestamp") from None


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON keys before dictionaries can silently discard evidence."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError("duplicate_json_key")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    """Reject nonstandard JSON numeric constants without echoing their contents."""
    raise EvidenceError("invalid_json_constant")


def json_value(data: bytes | str) -> Any:
    """Decode strict UTF8 JSON with duplicate/NaN/depth errors converted to safe codes."""
    try:
        return json.loads(
            data, object_pairs_hook=unique_object, parse_constant=reject_constant
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise EvidenceError("invalid_json") from None


@dataclass(frozen=True)
class Event:
    """Private normalized event; raw identifiers/message/timestamp stay out of repr."""

    line: int
    values: tuple[str, ...] = field(repr=False)

    @classmethod
    def parse(cls, value: object, line: int) -> Event:
        """Validate exactly six string fields, limits and kind; retain source time separately."""
        if not isinstance(value, dict) or set(value) != set(FIELDS):
            raise EvidenceError("event_schema", line)
        if any(
            not isinstance(value[name], str)
            or not value[name]
            or len(value[name]) > (4096 if name == "message" else 256)
            or "\x00" in value[name]
            for name in FIELDS
        ):
            raise EvidenceError("event_field", line)
        if value["kind"] not in KINDS:
            raise EvidenceError("event_kind", line)
        try:
            for name in FIELDS:
                value[name].encode("utf-8")
        except UnicodeError:
            raise EvidenceError("event_unicode", line) from None
        return cls(
            line,
            (
                value["event_id"],
                utc(value["timestamp"]),
                value["timestamp"],
                value["kind"],
                value["actor"],
                value["asset"],
                value["message"],
            ),
        )

    def committed(self) -> list[str | int]:
        """Return private canonical fields with source line, only for integrity commitments."""
        return [self.line, *self.values]
