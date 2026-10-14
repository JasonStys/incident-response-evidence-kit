"""Allowlisted pseudonymized JSON/CSV/inert HTML; raw messages never enter exports. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: reference — line 55
# parameter: domain — line 55
# parameter: key — line 55
# parameter: value — line 55
# definition: spreadsheet_cell — line 64
# parameter: value — line 64
# definition: html_report — line 74
# parameter: report — line 74
# variable: columns — line 76
# variable: rows — line 77
# variable: column — line 79
# variable: row — line 81
# variable: column — line 86
# definition: export — line 93
# parameter: case — line 94
# parameter: output — line 95
# parameter: checkpoint — line 96
# parameter: kind — line 98
# parameter: start — line 99
# parameter: end — line 100
# parameter: limit — line 101
# variable: connection — line 104
# variable: verified — line 105
# variable: key — line 106
# variable: count — line 107
# variable: more — line 107
# variable: rows — line 107
# variable: report — line 110
# variable: row — line 127
# variable: output — line 130
# variable: stream — line 133
# variable: columns — line 134
# variable: writer — line 135
# variable: event — line 137
# variable: column — line 138
# END CODE MAP

from __future__ import annotations

import csv
import hashlib
import hmac
import io
from html import escape
from pathlib import Path
from typing import Any

from .contracts import canonical
from .files import new_directory, write_new
from .store import Case


def reference(key: bytes, domain: str, value: str) -> str:
    """Create a case-specific HMAC-SHA256 pseudonym; domain separates actors/assets/evidence/cases."""
    return (
        domain
        + "-"
        + hmac.new(key, canonical([domain, value]), hashlib.sha256).hexdigest()[:24]
    )


def spreadsheet_cell(value: str) -> str:
    """Prefix formula-like cells as defense-in-depth; approved export values are already constrained."""
    return (
        "'" + value
        if value.lstrip().startswith(("=", "+", "-", "@"))
        or value.startswith(("\t", "\r", "\n"))
        else value
    )


def html_report(report: dict[str, Any]) -> str:
    """Render only the fixed export schema with escaping and no scripts, remote assets or active content."""
    columns = ("utc", "kind", "actor", "asset", "evidence", "line")
    rows = "".join(
        "<tr>"
        + "".join(f"<td>{escape(str(row[column]))}</td>" for column in columns)
        + "</tr>"
        for row in report["timeline"]
    )
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'"><title>Incident evidence timeline — Jason Stys</title><style>body{font:16px system-ui;background:#101b2d;color:#e4edf7;max-width:1200px;margin:2rem auto;padding:0 1rem}a{color:#90c7ff}table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:.6rem;border:1px solid #53667e;overflow-wrap:anywhere}section{overflow:auto}h1{color:#a6d9fd}</style><h1>Incident response evidence</h1><p>Created by Jason Stys · <a href="https://github.com/JasonStys">GitHub/contact</a> · <a href="https://www.linkedin.com/in/jason-stys-31b30b351/">LinkedIn</a></p><p>Pseudonymized review copy, not anonymized. Original messages and identities are omitted. Event times and patterns may still identify people. Review before sharing.</p>'
        + f'<p>Integrity checked: yes · Independent checkpoint supplied: {escape(str(report["anchored"]))} · Total events: {escape(str(report["total_events"]))} · Filter matches: {escape(str(report["filter_matches"]))} · Shown: {len(report["timeline"])} · More available: {escape(str(report["more_available"]))}</p><section aria-label="Scrollable normalized timeline"><table><caption>UTC ordering with deterministic evidence/record tie-breaks; source clocks are not independently verified.</caption><thead><tr>'
        + "".join(f'<th scope="col">{column}</th>' for column in columns)
        + "</tr></thead><tbody>"
        + rows
        + "</tbody></table></section></html>"
    )


def export(
    case: Case,
    output: Path,
    checkpoint: object = None,
    *,
    kind: str | None = None,
    start: str | None = None,
    end: str | None = None,
    limit: int = 1000,
) -> dict[str, Any]:
    """Verify a consistent read snapshot, project only approved fields, write a new directory; no uploads."""
    with case.connection() as connection:
        verified = case._verify(connection, checkpoint)
        key = connection.execute("SELECT pseudonym_key FROM metadata").fetchone()[0]
        rows, count, more = case.timeline(
            connection, kind=kind, start=start, end=end, limit=limit
        )
        report = {
            "schema": 1,
            "author": "Jason Stys",
            "case_ref": reference(key, "case", verified["case_id"]),
            "anchored": verified["anchored"],
            "total_events": verified["events"],
            "filter_matches": count,
            "more_available": more,
            "timeline": [
                {
                    "utc": row[0],
                    "evidence": reference(key, "evidence", row[1]),
                    "line": row[2],
                    "kind": row[3],
                    "actor": reference(key, "actor", row[4]),
                    "asset": reference(key, "asset", row[5]),
                }
                for row in rows
            ],
        }
    output = new_directory(output)
    write_new(output / "report.json", canonical(report) + b"\n")
    write_new(output / "report.html", html_report(report).encode("utf-8"))
    stream = io.StringIO(newline="")
    columns = ("utc", "kind", "actor", "asset", "evidence", "line")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(columns)
    for event in report["timeline"]:
        writer.writerow([spreadsheet_cell(str(event[column])) for column in columns])
    write_new(output / "timeline.csv", stream.getvalue().encode("utf-8"))
    return report
