"""Actual case acquisition, private keyset timelines and minimized handoffs for the native workbench. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 119
# variable: PRODUCT — line 120
# variable: PROFILE — line 120
# variable: TITLE — line 121
# variable: VERSION — line 121
# variable: COLUMNS — line 122
# variable: RESOURCES — line 128
# variable: MODES — line 136
# variable: REVIEW_MODE — line 147
# variable: CHOICES — line 148
# variable: FIELDS — line 154
# variable: BASE — line 195
# variable: FILTER — line 196
# variable: ACTIVE_FIELDS — line 197
# variable: SCENARIOS — line 217
# variable: HELP — line 226
# definition: scenario — line 234
# parameter: name — line 234
# variable: index — line 238
# variable: mode — line 239
# definition: case_path — line 263
# parameter: create — line 264
# parameter: parameters — line 264
# parameter: state — line 264
# variable: alias — line 273
# variable: n — line 279
# variable: n — line 280
# variable: parent — line 283
# variable: _ — line 287
# definition: checkpoint — line 294
# parameter: parameters — line 294
# variable: selected — line 296
# definition: filters — line 300
# parameter: parameters — line 300
# variable: text — line 302
# definition: bundle — line 315
# parameter: value — line 315
# variable: raw — line 317
# variable: page — line 318
# definition: analyze — line 326
# parameter: parameters — line 327
# parameter: stage — line 327
# parameter: state — line 327
# variable: mode — line 330
# variable: value — line 333
# variable: name — line 337
# variable: parameters — line 337
# variable: pin — line 344
# variable: root — line 345
# variable: case — line 347
# variable: case — line 349
# variable: selected_filter — line 350
# variable: value — line 351
# variable: result — line 371
# variable: path — line 377
# variable: selections — line 381
# variable: line — line 387
# variable: result — line 399
# variable: path — line 406
# variable: template — line 410
# variable: files — line 411
# variable: cursor — line 419
# variable: cursor — line 421
# variable: connection — line 422
# variable: verified — line 423
# variable: position — line 435
# variable: cursor — line 438
# variable: count — line 439
# variable: more — line 439
# variable: rows — line 439
# variable: row — line 454
# variable: files — line 468
# variable: key — line 476
# variable: verified — line 482
# definition: views — line 490
# parameter: files — line 490
# variable: value — line 493
# variable: item — line 497
# variable: key — line 497
# variable: name — line 500
# variable: value — line 501
# variable: item — line 505
# variable: key — line 505
# definition: cells — line 510
# parameter: row — line 510
# definition: next_page — line 524
# parameter: files — line 524
# variable: value — line 526
# definition: prepare_selected — line 532
# parameter: identity — line 533
# parameter: row — line 533
# parameter: state — line 533
# variable: files — line 536
# variable: connection — line 537
# variable: record — line 538
# variable: parameters — line 543
# variable: key — line 546
# variable: value — line 546
# variable: value — line 552
# END CODE MAP

from __future__ import annotations

import html
import re
import sys
from contextlib import closing
from pathlib import Path
from typing import Any

from . import bookmarks, report
from .contracts import KINDS
from .desktop_io import Rejected, canonical, json_value, read_bytes
from .desktop_state import Workspace, unlinked
from .store import Case

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
PRODUCT, PROFILE = "incident-response-evidence-kit", "IncidentResponseEvidenceKit"
TITLE, VERSION = "Incident Response Evidence Workbench", "1.1.1"
COLUMNS = (
    "UTC / operation",
    "Event / count",
    "Source line / integrity",
    "Privacy / context",
)
RESOURCES = (
    "sql/schema.sql",
    "examples/access-review.jsonl",
    "examples/service-change.csv",
    "notices.txt",
    "app.ico",
    "python314.dll",
)
MODES = (
    "Create a new private case",
    "Collect authorized source file",
    "Inspect private timeline",
    "Verify case integrity",
    "Record custody assertion",
    "Save private checkpoint",
    "Export minimized timeline",
    "Prepare private bookmark template",
    "Export selected bookmark handoff",
)
REVIEW_MODE = "timeline-navigation"
CHOICES = {
    "format": ("jsonl", "csv", "opaque"),
    "kind": ("all", *sorted(KINDS)),
    "action": ("review", "handoff"),
    "tag": ("key-event", "follow-up", "needs-context", "reviewed"),
}
FIELDS = (
    (
        "alias",
        "Managed case name (new case: lowercase letters, numbers, hyphens)",
        "text",
    ),
    (
        "case",
        "Existing authorized case directory (blank uses managed name)",
        "directory",
    ),
    (
        "operator",
        "Nonidentifying operator reference (assertion, not authentication)",
        "text",
    ),
    ("clock", "Custody assertion UTC clock (explicit offset required)", "text"),
    ("source", "Nonidentifying source reference", "text"),
    ("input", "Authorized original source file (copied into private case)", "file"),
    ("format", "Supported source format", "choice"),
    ("checkpoint", "Optional private checkpoint JSON (required for bookmarks)", "file"),
    ("kind", "Event kind filter", "choice"),
    ("start", "Start time inclusive (blank: unbounded; explicit offset)", "text"),
    ("end", "End time exclusive (blank: unbounded; explicit offset)", "text"),
    ("limit", "Page size (1–1000); full matching count retained", "text"),
    ("cursor", "Next-page JSON cursor (use Prepare next timeline page)", "text"),
    ("digest", "Exact source SHA256 for custody assertion", "text"),
    ("action", "Custody assertion type", "choice"),
    (
        "selections",
        "Optional private bookmark JSON (blank: selected event fields below)",
        "file",
    ),
    ("line", "Exact original source line (positive integer)", "text"),
    ("tag", "Selected-event review tag", "choice"),
    (
        "note",
        "Private note (1–500 printable characters; omitted from handoff)",
        "text",
    ),
)
BASE = ("alias", "case")
FILTER = ("kind", "start", "end", "limit")
ACTIVE_FIELDS = {
    MODES[0]: ("alias", "operator", "clock"),
    MODES[1]: (*BASE, "operator", "clock", "source", "input", "format"),
    MODES[2]: (*BASE, "checkpoint", *FILTER, "cursor"),
    MODES[3]: (*BASE, "checkpoint"),
    MODES[4]: (*BASE, "operator", "clock", "digest", "action"),
    MODES[5]: BASE,
    MODES[6]: (*BASE, "checkpoint", *FILTER),
    MODES[7]: (*BASE, "checkpoint"),
    MODES[8]: (
        *BASE,
        "checkpoint",
        "selections",
        "digest",
        "line",
        "tag",
        "operator",
        "note",
    ),
}
SCENARIOS = (
    "1  Create fictional access-review case",
    "2  Collect fictional access JSONL",
    "3  Collect fictional service CSV",
    "4  Inspect two-event timeline page",
    "5  Verify preserved original bytes",
    "6  Save private checkpoint",
    "7  Export minimized five-event timeline",
)
HELP = """Preserve authorized originals in a private case, verify custody and inspect normalized UTC events.
Create a new managed case, collect JSONL/CSV/opaque files, then inspect/verify. Prepared steps use the same ordinary controls and real core.
The private timeline exposes original identifiers and source hashes; minimized timeline/handoff exports omit them. Generic bundle export can still contain PRIVATE checkpoint or timeline data: read its file list before sharing.
Use Prepare next timeline page on a saved timeline; its cursor binds case/head and filters. Select an event and Prepare selected bookmark, then supply a checkpoint exported from Save private checkpoint. Private notes are omitted from the resulting handoff.
A checkpoint kept in this same profile is NOT independently stored. Copy it to separately trusted storage for a real external prefix anchor. Custody clocks/operators and event clocks remain assertions, not authenticated people or forensic/legal certification.
Managed cases keep original plaintext evidence, at most eight case directories with the original per-case 64 MiB raw-data cap. Removing a saved analysis NEVER removes a case. External CLI case paths remain supported. Back up closed cases separately; there is no automatic deletion or host collection."""


def scenario(name: str) -> dict[str, str]:
    """Populate ordinary controls; the ordered fictional scenario never creates or collects data until Run."""
    if name not in SCENARIOS:
        raise Rejected("unknown prepared evidence scenario")
    index = SCENARIOS.index(name)
    mode = (0, 1, 1, 2, 3, 5, 6)[index]
    return {
        "mode": MODES[mode],
        "alias": "fictional-access-review",
        "operator": "analyst-demo",
        "clock": "2026-10-10T16:03:00Z",
        "source": "authorized-fictional-training",
        "input": str(
            ROOT
            / (
                "examples/service-change.csv"
                if index == 2
                else "examples/access-review.jsonl"
            )
        ),
        "format": "csv" if index == 2 else "jsonl",
        "kind": "all",
        "limit": "2" if index == 3 else "1000",
        "action": "review",
        "tag": "needs-context",
        "note": "Fictional selected event requires human context.",
    }


def case_path(
    state: Workspace, parameters: dict[str, str], *, create: bool = False
) -> Path:
    """Resolve one explicit existing CLI case or a bounded app-managed new case, rejecting links/reserved names."""
    if parameters.get("case", "").strip():
        if create:
            raise Rejected(
                "create uses a new managed case name; existing cases are never reset"
            )
        return unlinked(Path(parameters["case"]))
    alias = parameters.get("alias", "")
    if re.fullmatch(r"[a-z][a-z0-9-]{0,39}", alias) is None or alias in {
        "con",
        "prn",
        "aux",
        "nul",
        *(f"com{n}" for n in range(1, 10)),
        *(f"lpt{n}" for n in range(1, 10)),
    }:
        raise Rejected("invalid managed case name")
    parent = unlinked(state.path / "cases")
    parent.mkdir(exist_ok=True, mode=0o700)
    if not parent.is_dir():
        raise Rejected("managed cases path is not a directory")
    if create and sum(1 for _ in parent.iterdir()) >= 8:
        raise Rejected(
            "eight managed cases already exist; preserve closed case backups outside this profile"
        )
    return unlinked(parent / alias)


def checkpoint(parameters: dict[str, str]) -> object:
    """Read an explicitly selected bounded checkpoint without asserting its independent storage."""
    selected = parameters.get("checkpoint", "").strip()
    return json_value(read_bytes(Path(selected), 4096)) if selected else None


def filters(parameters: dict[str, str]) -> dict[str, Any]:
    """Supply original timeline filters; numeric syntax cannot silently coerce booleans or fractions."""
    text = parameters.get("limit", "1000")
    if not text.isascii() or not text.isdecimal() or not 1 <= int(text) <= 1000:
        raise Rejected("page size must be an integer from 1 to 1000")
    return {
        "kind": None
        if parameters.get("kind") in (None, "", "all")
        else parameters["kind"],
        "start": parameters.get("start") or None,
        "end": parameters.get("end") or None,
        "limit": int(text),
    }


def bundle(value: dict[str, Any]) -> dict[str, bytes]:
    """Retain bounded private structured inspection and inert escaped HTML; never duplicate original BLOBs."""
    raw = canonical(value)
    page = (
        "<!doctype html><html lang='en'><meta charset='utf-8'><meta http-equiv='Content-Security-Policy' content=\"default-src 'none'; base-uri 'none'; form-action 'none'\"><title>Private evidence inspection — Jason Stys</title><h1>Private evidence inspection</h1><p>Contains private metadata; not a minimized handoff.</p><pre>"
        + html.escape(raw.decode())
        + "</pre></html>"
    )
    return {"result.json": raw + b"\n", "result.html": page.encode()}


def analyze(
    state: Workspace, parameters: dict[str, str], stage: Path
) -> tuple[str, str, dict[str, bytes]]:
    """Run original transactional methods; case mutations commit independently of optional GUI history retention."""
    mode = parameters.get("mode", "")
    if mode not in MODES:
        raise Rejected("unsupported offline case operation")
    if sum(len(value.encode("utf8")) for value in parameters.values()) > 512 * 1024:
        raise Rejected("desktop parameter text exceeds its limit")
    # The UI deliberately retains hidden fields between operations. Only the
    # selected operation's visible inputs may influence its actual Case call.
    parameters = {name: parameters.get(name, "") for name in ACTIVE_FIELDS[mode]}
    # A full history fails before any case mutation; storage/I/O failures may still
    # occur after a valid core commit. The UI explicitly instructs Verify on retry.
    if len(state.history()) >= 20:
        raise Rejected(
            "history is full; export and explicitly remove a saved analysis first"
        )
    pin = checkpoint(parameters)
    root = case_path(state, parameters, create=mode == MODES[0])
    if mode == MODES[0]:
        case = Case.create(root, parameters["operator"], parameters["clock"])
    else:
        case = Case(root)
    selected_filter = filters(parameters) if mode in (MODES[2], MODES[6]) else {}
    value: dict[str, Any] = {
        "operation": mode,
        "privacy": "PRIVATE: contains case identifiers/source hashes; not a minimized handoff",
    }
    if mode == MODES[1]:
        value["collected_sha256"] = case.collect(
            Path(parameters["input"]),
            parameters["format"],
            parameters["operator"],
            parameters["source"],
            parameters["clock"],
        )
    elif mode == MODES[4]:
        case.record(
            parameters["digest"],
            parameters["action"],
            parameters["operator"],
            parameters["clock"],
        )
    elif mode == MODES[6]:
        result = report.export(case, stage / "minimized", pin, **selected_filter)
        return (
            mode,
            f"Minimized {len(result['timeline'])}/{result['filter_matches']} matching events; pseudonymized, not anonymous",
            {
                path.name: read_bytes(path, 32 * 1024 * 1024)
                for path in (stage / "minimized").iterdir()
            },
        )
    elif mode == MODES[8]:
        selections = (
            json_value(read_bytes(Path(parameters["selections"]), 4 * 1024 * 1024))
            if parameters.get("selections", "").strip()
            else bookmarks.template(case, pin)
        )
        if not parameters.get("selections", "").strip():
            line = parameters.get("line", "")
            if not line.isascii() or not line.isdecimal():
                raise Rejected("selected original line must be a positive integer")
            selections["entries"] = [
                {
                    "evidence_sha256": parameters["digest"],
                    "line": int(line),
                    "tag": parameters["tag"],
                    "note": parameters["note"],
                    "operator": parameters["operator"],
                }
            ]
        result = bookmarks.review(case, selections, pin)
        bookmarks.export(result, stage / "handoff")
        return (
            mode,
            f"Minimized {len(result['timeline'])} exact selected events; private notes/operators omitted",
            {
                path.name: read_bytes(path, 32 * 1024 * 1024)
                for path in (stage / "handoff").iterdir()
            },
        )
    elif mode == MODES[7]:
        template = bookmarks.template(case, pin)
        files = bundle({**value, "records": [template]})
        files["private-bookmarks.json"] = canonical(template) + b"\n"
        return (
            mode,
            "Private current-head selection template; not a minimized handoff",
            files,
        )
    if mode == MODES[2]:
        cursor = None
        if parameters.get("cursor", "").strip():
            cursor = json_value(parameters["cursor"].encode())
        with case.connection() as connection:
            verified = case._verify(connection, pin)
            if cursor is not None:
                if (
                    not isinstance(cursor, dict)
                    or set(cursor) != {"case_id", "head", "filters", "position"}
                    or cursor["case_id"] != verified["case_id"]
                    or cursor["head"] != verified["head"]
                    or cursor["filters"] != selected_filter
                ):
                    raise Rejected(
                        "timeline cursor is stale or belongs to different case/filters"
                    )
                position = cursor["position"]
                if not isinstance(position, list):
                    raise Rejected("invalid timeline cursor position")
                cursor = tuple(position)
            rows, count, more = case.timeline(
                connection, cursor=cursor, **selected_filter
            )
        value.update(
            verification=verified,
            filter_matches=count,
            more_available=more,
            records=[
                dict(
                    zip(
                        ("utc", "evidence_sha256", "line", "kind", "actor", "asset"),
                        row,
                        strict=True,
                    )
                )
                for row in rows
            ],
            next_cursor={
                "case_id": verified["case_id"],
                "head": verified["head"],
                "filters": selected_filter,
                "position": list(rows[-1][:3]),
            }
            if more and rows
            else None,
        )
    else:
        value["verification"] = case.verify(pin)
        value["records"] = [value["verification"]]
    files = bundle(value)
    if mode == MODES[5]:
        files["private-checkpoint.json"] = (
            canonical(
                {
                    "schema": 1,
                    **{
                        key: value["verification"][key]
                        for key in ("case_id", "seq", "head")
                    },
                }
            )
            + b"\n"
        )
    verified = value["verification"]
    return (
        mode,
        f"{verified['files']} preserved files / {verified['events']} events / custody {verified['seq']}; private inspection",
        files,
    )


def views(files: dict[str, bytes]) -> dict[str, list[dict[str, Any]]]:
    """Keep private original timeline details separate from explicitly minimized output projections."""
    if "result.json" in files:
        value = json_value(files["result.json"])
        return {
            "Private records — do not share": value["records"],
            "Private verification and pagination": [
                {key: item for key, item in value.items() if key != "records"}
            ],
        }
    name = "report.json" if "report.json" in files else "handoff.json"
    value = json_value(files[name])
    return {
        "Minimized pseudonymized events": value["timeline"],
        "Minimized scope and counts": [
            {key: item for key, item in value.items() if key != "timeline"}
        ],
    }


def cells(row: dict[str, Any]) -> tuple[str, str, str, str]:
    """Show exact UTC/source record references, keeping the complete selected record copyable."""
    return (
        str(row.get("utc", "Case / scope")),
        str(row.get("kind", row.get("events", row.get("operation", "inspection")))),
        str(row.get("line", row.get("head", "counts and limits"))),
        str(
            row.get(
                "actor", row.get("case_id", row.get("privacy", "minimized projection"))
            )
        ),
    )


def next_page(files: dict[str, bytes]) -> str:
    """Prepare a bound cursor only from a completed original timeline page with more results."""
    value = json_value(files.get("result.json", b"{}"))
    if value.get("operation") != MODES[2] or not value.get("next_cursor"):
        raise Rejected("select a private timeline page with more events first")
    return canonical(value["next_cursor"]).decode()


def prepare_selected(
    state: Workspace, identity: int, row: dict[str, Any] | None = None
) -> dict[str, str]:
    """Restore saved input context for a deliberate next page or original-source bookmark, never execute it automatically."""
    files = state.files(identity)
    with closing(state.connect()) as connection:
        record = connection.execute(
            "SELECT parameters FROM run WHERE id=?", (identity,)
        ).fetchone()
    if record is None:
        raise Rejected("select a saved timeline first")
    parameters = json_value(record[0].encode())
    if not isinstance(parameters, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in parameters.items()
    ):
        raise Rejected("saved timeline parameters are malformed")
    if row is None:
        parameters.update(mode=MODES[2], cursor=next_page(files))
    else:
        value = json_value(files.get("result.json", b"{}"))
        if value.get("operation") != MODES[2] or row not in value["records"]:
            raise Rejected(
                "select an original private timeline event; minimized references cannot identify source bytes"
            )
        parameters.update(
            mode=MODES[8],
            digest=row["evidence_sha256"],
            line=str(row["line"]),
            selections="",
            tag="needs-context",
            note="Add a private human review note.",
            operator=parameters.get("operator") or "analyst-local",
        )
    return parameters
