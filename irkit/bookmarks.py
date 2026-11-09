"""Exact evidence-line annotations and minimized checkpoint-bound handoff. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: TAGS — line 50
# definition: template — line 53
# parameter: case — line 53
# parameter: checkpoint — line 53
# variable: verified — line 57
# definition: review — line 67
# parameter: case — line 67
# parameter: checkpoint — line 67
# parameter: selections — line 67
# variable: entries — line 79
# variable: connection — line 82
# variable: verified — line 83
# variable: name — line 85
# variable: key — line 88
# variable: rows — line 89
# variable: seen — line 90
# variable: entry — line 91
# variable: digest — line 100
# variable: line — line 100
# variable: note — line 113
# variable: char — line 120
# variable: event — line 124
# variable: name — line 156
# parameter: row — line 165
# definition: export — line 171
# parameter: output — line 171
# parameter: result — line 171
# variable: columns — line 173
# variable: rows — line 174
# variable: column — line 176
# variable: row — line 178
# variable: page — line 180
# variable: column — line 182
# variable: output — line 189
# END CODE MAP

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from .contracts import DIGEST, MAX_EVENTS, EvidenceError, canonical, token
from .files import new_directory, write_new
from .report import reference
from .store import Case

TAGS = {"key-event", "follow-up", "needs-context", "reviewed"}


def template(case: Case, checkpoint: object) -> dict[str, Any]:
    """Make a private blank sidecar bound to current verified case state and an explicit prefix checkpoint."""
    if checkpoint is None:
        raise EvidenceError("checkpoint_required")
    verified = case.verify(checkpoint)
    return {
        "schema": 1,
        "case_id": verified["case_id"],
        "seq": verified["seq"],
        "head": verified["head"],
        "entries": [],
    }


def review(case: Case, selections: Any, checkpoint: object) -> dict[str, Any]:
    """Resolve <=1000 unique exact original digest/line bookmarks in one reverified read transaction."""
    if checkpoint is None:
        raise EvidenceError("checkpoint_required")
    if (
        not isinstance(selections, dict)
        or set(selections) != {"schema", "case_id", "seq", "head", "entries"}
        or type(selections["schema"]) is not int
        or selections["schema"] != 1
        or type(selections["seq"]) is not int
    ):
        raise EvidenceError("bookmark_contract")
    entries = selections["entries"]
    if not isinstance(entries, list) or not 1 <= len(entries) <= 1000:
        raise EvidenceError("bookmark_bound")
    with case.connection() as connection:
        verified = case._verify(connection, checkpoint)
        if any(
            selections[name] != verified[name] for name in ("case_id", "seq", "head")
        ):
            raise EvidenceError("bookmark_snapshot_mismatch")
        key = connection.execute("SELECT pseudonym_key FROM metadata").fetchone()[0]
        rows = []
        seen = set()
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {
                "evidence_sha256",
                "line",
                "tag",
                "note",
                "operator",
            }:
                raise EvidenceError("bookmark_fields")
            digest, line = entry["evidence_sha256"], entry["line"]
            if (
                not isinstance(digest, str)
                or not DIGEST.fullmatch(digest)
                or type(line) is not int
                or not 1 <= line <= MAX_EVENTS
                or (digest, line) in seen
            ):
                raise EvidenceError("bookmark_reference")
            seen.add((digest, line))
            if not isinstance(entry["tag"], str) or entry["tag"] not in TAGS:
                raise EvidenceError("bookmark_tag")
            token(entry["operator"])
            note = entry["note"]
            if (
                not isinstance(note, str)
                or not note.strip()
                or len(note) > 500
                or any(
                    ord(char) < 32 or ord(char) == 127 or 0xD800 <= ord(char) <= 0xDFFF
                    for char in note
                )
            ):
                raise EvidenceError("bookmark_note")
            event = connection.execute(
                "SELECT utc,kind,actor,asset FROM events WHERE evidence_digest=? AND line=?",
                (digest, line),
            ).fetchone()
            if event is None:
                raise EvidenceError("bookmark_event_not_found")
            rows.append(
                {
                    "utc": event[0],
                    "kind": event[1],
                    "actor": reference(key, "actor", event[2]),
                    "asset": reference(key, "asset", event[3]),
                    "evidence": reference(key, "evidence", digest),
                    "line": line,
                    "tag": entry["tag"],
                    "annotation_ref": reference(
                        key, "annotation", canonical(entry).decode()
                    ),
                }
            )
        return {
            "schema": 1,
            "kind": "minimized_bookmark_handoff",
            "author": "Jason Stys",
            "case_ref": reference(key, "case", verified["case_id"]),
            "checkpoint_ref": reference(
                key, "checkpoint", canonical(checkpoint).decode()
            ),
            "snapshot_ref": reference(
                key,
                "snapshot",
                canonical(
                    {name: verified[name] for name in ("case_id", "seq", "head")}
                ).decode(),
            ),
            "selections_ref": reference(
                key, "selections", canonical(selections).decode()
            ),
            "checkpoint_matched": True,
            "total_events": verified["events"],
            "timeline": sorted(
                rows, key=lambda row: (row["utc"], row["evidence"], row["line"])
            ),
            "scope": "Pseudonymized selected events and tags only; private notes/operators/originals/messages/source hashes are omitted. Not anonymized, an incident verdict, authenticated analyst identity or proof of independent checkpoint storage.",
        }


def export(result: dict[str, Any], output: Path) -> None:
    """Save only minimized review material; private selection notes stay in the caller's original sidecar."""
    columns = ("utc", "kind", "tag", "actor", "asset", "evidence", "line")
    rows = "".join(
        "<tr>"
        + "".join(f"<td>{html.escape(str(row[column]))}</td>" for column in columns)
        + "</tr>"
        for row in result["timeline"]
    )
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; base-uri \'none\'; form-action \'none\'"><title>Selected evidence handoff — Jason Stys</title><main><h1>Bookmarked event handoff</h1><p>Created by Jason Stys. Pseudonymized, not anonymized; private notes and originals omitted.</p><table><caption>Verified selected original evidence lines; source clocks remain assertions</caption><tr>'
        + "".join(f"<th>{column}</th>" for column in columns)
        + "</tr>"
        + rows
        + "</table><details><summary>Minimized checkpoint/snapshot references and limits</summary><pre>"
        + html.escape(canonical(result).decode())
        + "</pre></details></main></html>"
    )
    output = new_directory(output)
    write_new(output / "handoff.json", canonical(result) + b"\n")
    write_new(output / "handoff.html", page.encode("utf-8"))
