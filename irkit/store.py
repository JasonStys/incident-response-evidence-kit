"""Transactional private evidence, anchored custody checks and stable keyset timelines. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: SCHEMA — line 171
# variable: ZERO — line 172
# variable: VM_STEPS — line 173
# variable: REQUIRED_TABLES — line 174
# definition: schema_hash — line 177
# parameter: connection — line 177
# definition: append — line 188
# parameter: connection — line 188
# parameter: payload — line 188
# variable: row — line 190
# variable: previous — line 193
# variable: sequence — line 193
# variable: digest — line 196
# definition: Case — line 204
# definition: __init__ — line 207
# parameter: root — line 207
# parameter: self — line 207
# attribute: root — line 209
# attribute: database — line 210
# definition: create — line 219
# parameter: cls — line 219
# parameter: operator — line 219
# parameter: root — line 219
# parameter: timestamp — line 219
# variable: operator — line 221
# variable: timestamp — line 221
# variable: root — line 222
# variable: case — line 224
# variable: connection — line 225
# variable: case_id — line 230
# variable: key — line 230
# definition: connection — line 248
# parameter: _initialize — line 249
# parameter: self — line 249
# parameter: write — line 249
# variable: suffix — line 253
# variable: connection — line 255
# variable: remaining — line 265
# definition: progress — line 267
# variable: remaining — line 270
# variable: objects — line 278
# variable: tables — line 285
# variable: _ — line 287
# variable: kind — line 287
# variable: name — line 287
# variable: schema — line 287
# definition: _verify — line 302
# parameter: checkpoint — line 303
# parameter: connection — line 303
# parameter: self — line 303
# definition: _inspect — line 313
# parameter: checkpoint — line 314
# parameter: connection — line 314
# parameter: self — line 314
# variable: metadata — line 324
# variable: case_id — line 327
# variable: key — line 327
# variable: char — line 331
# variable: event_count — line 336
# variable: count — line 337
# variable: size — line 337
# variable: commitments — line 342
# variable: digest — line 343
# variable: events_digest — line 343
# variable: format_name — line 343
# variable: raw — line 343
# variable: normalized — line 353
# variable: actual — line 354
# variable: event — line 358
# variable: expected — line 358
# variable: row — line 359
# variable: custody — line 369
# variable: previous — line 374
# variable: collected — line 375
# variable: encoded — line 376
# variable: expected_seq — line 376
# variable: head — line 376
# variable: old — line 376
# variable: sequence — line 376
# variable: payload — line 377
# variable: expected_genesis — line 393
# variable: digest — line 405
# variable: previous — line 430
# definition: verify — line 460
# parameter: checkpoint — line 460
# parameter: self — line 460
# variable: connection — line 462
# definition: collect — line 465
# parameter: format_name — line 466
# parameter: operator — line 466
# parameter: path — line 466
# parameter: self — line 466
# parameter: source — line 466
# parameter: timestamp — line 466
# variable: operator — line 469
# variable: source — line 469
# variable: timestamp — line 469
# variable: raw — line 470
# variable: events — line 471
# variable: digest — line 472
# variable: event_digest — line 472
# variable: event — line 474
# variable: connection — line 476
# variable: verified — line 477
# variable: existing — line 478
# variable: event — line 497
# definition: record — line 515
# parameter: action — line 515
# parameter: digest — line 515
# parameter: operator — line 515
# parameter: self — line 515
# parameter: timestamp — line 515
# variable: operator — line 517
# variable: timestamp — line 517
# variable: connection — line 524
# definition: checkpoint — line 540
# parameter: path — line 540
# parameter: self — line 540
# variable: verified — line 542
# variable: key — line 546
# definition: timeline — line 551
# parameter: self — line 552
# parameter: connection — line 553
# parameter: kind — line 555
# parameter: start — line 556
# parameter: end — line 557
# parameter: limit — line 558
# parameter: cursor — line 559
# variable: end — line 569
# variable: start — line 569
# variable: clauses — line 575
# variable: parameters — line 576
# variable: clause — line 577
# variable: value — line 577
# variable: where — line 581
# variable: count — line 582
# variable: where — line 594
# variable: rows — line 596
# END CODE MAP

from __future__ import annotations

import hmac
import secrets
import sqlite3
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .contracts import (
    DIGEST,
    KINDS,
    MAX_CASE,
    MAX_CUSTODY,
    MAX_EVENTS,
    MAX_FILE,
    EvidenceError,
    canonical,
    json_value,
    sha,
    token,
    utc,
)
from .files import checked_path, new_directory, read_file, write_new
from .parsing import parse

SCHEMA = Path(__file__).resolve().parents[1] / "sql" / "schema.sql"
ZERO = "0" * 64
VM_STEPS = 20_000_000
REQUIRED_TABLES = frozenset({"metadata", "evidence", "events", "custody"})


def schema_hash(connection: sqlite3.Connection) -> str:
    """Commit sorted application schema/trigger/index SQL; SQLite internal tables are excluded."""
    return sha(
        canonical(
            connection.execute(
                "SELECT type,name,sql FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name"
            ).fetchall()
        )
    )


def append(connection: sqlite3.Connection, payload: dict[str, Any]) -> dict[str, Any]:
    """Append one canonical custody entry inside the caller's immediate write transaction."""
    row = connection.execute(
        "SELECT seq,head FROM custody ORDER BY seq DESC LIMIT 1"
    ).fetchone()
    sequence, previous = (row[0] + 1, row[1]) if row else (1, ZERO)
    if sequence > MAX_CUSTODY:
        raise EvidenceError("custody_limit")
    digest = sha(canonical([sequence, previous, payload]))
    connection.execute(
        "INSERT INTO custody VALUES(?,?,?,?)",
        (sequence, canonical(payload).decode(), previous, digest),
    )
    return {"seq": sequence, "head": digest}


class Case:
    """A trusted local directory with one private SQLite database; methods use separate connections."""

    def __init__(self, root: Path) -> None:
        """Select an existing case, checking link/device/size boundaries without creating files."""
        self.root = checked_path(root)
        self.database = checked_path(self.root / "case.sqlite")
        if (
            not self.root.is_dir()
            or not self.database.is_file()
            or self.database.stat().st_size > 256 * 1024 * 1024
        ):
            raise EvidenceError("invalid_case")

    @classmethod
    def create(cls, root: Path, operator: str, timestamp: str) -> Case:
        """Create a new case/genesis; caller supplies collection clock and operator reference."""
        operator, timestamp = token(operator), utc(timestamp)
        root = new_directory(root)
        write_new(root / "case.sqlite", b"")
        case = cls(root)
        with case.connection(write=True, _initialize=True) as connection:
            # executescript initializes only our reviewed SQL, never imported evidence.
            connection.executescript(SCHEMA.read_text(encoding="utf-8"))
            connection.execute("PRAGMA user_version=1")
            connection.execute("BEGIN IMMEDIATE")
            case_id, key = uuid.uuid4().hex, secrets.token_bytes(32)
            connection.execute("INSERT INTO metadata VALUES(?,?)", (case_id, key))
            append(
                connection,
                {
                    "action": "genesis",
                    "operator": operator,
                    "utc": timestamp,
                    "case_id": case_id,
                    "key_hash": sha(key),
                    "schema_hash": schema_hash(connection),
                    "version": 1,
                },
            )
        case.verify()
        return case

    @contextmanager
    def connection(
        self, *, write: bool = False, _initialize: bool = False
    ) -> Iterator[sqlite3.Connection]:
        """Open a bounded SQLite transaction; enable foreign keys, disable extension loading/trusted schema."""
        checked_path(self.database)
        for suffix in ("-journal", "-wal", "-shm"):
            checked_path(Path(str(self.database) + suffix))
        connection = sqlite3.connect(
            self.database.as_uri() + ("?mode=rw" if write else "?mode=ro"),
            uri=True,
            timeout=5,
            isolation_level=None,
        )
        try:
            # Imported databases are data, not trusted query plans. Bound SQLite before
            # any application-table query; a forged view must never run as a case.
            connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, MAX_FILE + 65536)
            remaining = VM_STEPS // 1000

            def progress() -> int:
                """Interrupt this connection after the documented finite VM budget."""
                nonlocal remaining
                remaining -= 1
                return int(remaining <= 0)

            connection.set_progress_handler(progress, 1000)
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA trusted_schema=OFF")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            objects = connection.execute(
                "SELECT name,type,sql FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%' LIMIT 65"
            ).fetchall()
            if _initialize:
                if not write or objects:
                    raise EvidenceError("case_initialization")
            else:
                tables = {
                    name
                    for schema, name, kind, *_ in connection.execute(
                        "PRAGMA table_list"
                    )
                    if schema == "main" and kind == "table"
                }
                if not REQUIRED_TABLES <= tables or len(objects) > 64:
                    raise EvidenceError("case_schema")
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _verify(
        self, connection: sqlite3.Connection, checkpoint: object = None
    ) -> dict[str, Any]:
        """Normalize corrupt database type/schema errors without revealing raw stored values."""
        try:
            return self._inspect(connection, checkpoint)
        except EvidenceError:
            raise
        except (TypeError, KeyError, ValueError, sqlite3.Error):
            raise EvidenceError("case_integrity") from None

    def _inspect(
        self, connection: sqlite3.Connection, checkpoint: object = None
    ) -> dict[str, Any]:
        """Rehash original BLOBs, reparse events, validate provenance and an optional independent prefix pin."""
        if (
            connection.execute("PRAGMA quick_check").fetchall() != [("ok",)]
            or connection.execute("PRAGMA foreign_key_check").fetchone()
        ):
            raise EvidenceError("database_integrity")
        if connection.execute("PRAGMA user_version").fetchone()[0] != 1:
            raise EvidenceError("case_version")
        metadata = connection.execute("SELECT * FROM metadata LIMIT 2").fetchall()
        if len(metadata) != 1:
            raise EvidenceError("metadata_integrity")
        case_id, key = metadata[0]
        if (
            not isinstance(case_id, str)
            or len(case_id) != 32
            or any(char not in "0123456789abcdef" for char in case_id)
            or not isinstance(key, bytes)
            or len(key) != 32
        ):
            raise EvidenceError("metadata_integrity")
        event_count = connection.execute("SELECT count(*) FROM events").fetchone()[0]
        count, size = connection.execute(
            "SELECT count(*),coalesce(sum(length(raw)),0) FROM evidence"
        ).fetchone()
        if event_count > MAX_EVENTS or count > 256 or size > MAX_CASE:
            raise EvidenceError("case_limits")
        commitments: dict[str, dict[str, Any]] = {}
        for digest, format_name, raw, events_digest in connection.execute(
            "SELECT * FROM evidence ORDER BY digest"
        ):
            if (
                not isinstance(raw, bytes)
                or not isinstance(digest, str)
                or not DIGEST.fullmatch(digest)
                or sha(raw) != digest
            ):
                raise EvidenceError("evidence_integrity")
            normalized = parse(raw, format_name)
            actual = connection.execute(
                "SELECT line,event_id,utc,source_time,kind,actor,asset,message FROM events WHERE evidence_digest=? ORDER BY line",
                (digest,),
            ).fetchall()
            expected = [event.committed() for event in normalized]
            if [list(row) for row in actual] != expected or sha(
                canonical(expected)
            ) != events_digest:
                raise EvidenceError("event_integrity")
            commitments[digest] = {
                "format": format_name,
                "bytes": len(raw),
                "events_digest": events_digest,
                "event_count": len(normalized),
            }
        custody = connection.execute(
            "SELECT * FROM custody ORDER BY seq LIMIT ?", (MAX_CUSTODY + 1,)
        ).fetchall()
        if not 1 <= len(custody) <= MAX_CUSTODY:
            raise EvidenceError("custody_limit")
        previous = ZERO
        collected: set[str] = set()
        for expected_seq, (sequence, encoded, old, head) in enumerate(custody, 1):
            payload = json_value(encoded)
            if (
                not isinstance(payload, dict)
                or sequence != expected_seq
                or canonical(payload).decode() != encoded
                or old != previous
                or not hmac.compare_digest(
                    head, sha(canonical([sequence, old, payload]))
                )
            ):
                raise EvidenceError("custody_integrity")
            if payload.get("utc") != utc(payload.get("utc")) or payload.get(
                "operator"
            ) != token(payload.get("operator")):
                raise EvidenceError("custody_integrity")
            if sequence == 1:
                expected_genesis = {
                    "action": "genesis",
                    "operator": payload["operator"],
                    "utc": payload["utc"],
                    "case_id": case_id,
                    "key_hash": sha(key),
                    "schema_hash": schema_hash(connection),
                    "version": 1,
                }
                if payload != expected_genesis:
                    raise EvidenceError("genesis_integrity")
            elif payload.get("action") == "collect":
                digest = payload.get("evidence")
                if (
                    not isinstance(digest, str)
                    or digest not in commitments
                    or digest in collected
                ):
                    raise EvidenceError("collection_integrity")
                if payload != {
                    "action": "collect",
                    "operator": payload["operator"],
                    "utc": payload["utc"],
                    "evidence": digest,
                    "source_code": token(payload.get("source_code")),
                    **commitments[digest],
                }:
                    raise EvidenceError("collection_integrity")
                collected.add(digest)
            elif payload.get("action") in {"review", "handoff"}:
                if (
                    set(payload) != {"action", "operator", "utc", "evidence"}
                    or payload["evidence"] not in collected
                ):
                    raise EvidenceError("collection_integrity")
            else:
                raise EvidenceError("custody_action")
            previous = head
        if collected != set(commitments):
            raise EvidenceError("untracked_evidence")
        if checkpoint is not None:
            if (
                not isinstance(checkpoint, dict)
                or set(checkpoint) != {"schema", "case_id", "seq", "head"}
                or type(checkpoint["schema"]) is not int
                or checkpoint["schema"] != 1
                or checkpoint["case_id"] != case_id
                or type(checkpoint["seq"]) is not int
                or not 1 <= checkpoint["seq"] <= len(custody)
                or not isinstance(checkpoint["head"], str)
                or not DIGEST.fullmatch(checkpoint["head"])
                or not hmac.compare_digest(
                    custody[checkpoint["seq"] - 1][3], checkpoint["head"]
                )
            ):
                raise EvidenceError("checkpoint_mismatch")
        return {
            "schema": 1,
            "case_id": case_id,
            "seq": len(custody),
            "head": previous,
            "files": count,
            "events": event_count,
            "bytes": size,
            "anchored": checkpoint is not None,
        }

    def verify(self, checkpoint: object = None) -> dict[str, Any]:
        """Return private integrity counts/pin; independent checkpoint detects anchored rewrites/truncation."""
        with self.connection() as connection:
            return self._verify(connection, checkpoint)

    def collect(
        self, path: Path, format_name: str, operator: str, source: str, timestamp: str
    ) -> str:
        """Acquire one authorized file, atomically commit bytes/events/provenance, dedupe byte-identical retries."""
        operator, source, timestamp = token(operator), token(source), utc(timestamp)
        raw = read_file(path)
        events = parse(raw, format_name)
        digest, event_digest = (
            sha(raw),
            sha(canonical([event.committed() for event in events])),
        )
        with self.connection(write=True) as connection:
            verified = self._verify(connection)
            existing = connection.execute(
                "SELECT format FROM evidence WHERE digest=?", (digest,)
            ).fetchone()
            if existing:
                if existing[0] != format_name:
                    raise EvidenceError("format_conflict")
                return digest
            if (
                verified["files"] >= 256
                or verified["bytes"] + len(raw) > MAX_CASE
                or verified["events"] + len(events) > MAX_EVENTS
            ):
                raise EvidenceError("case_limits")
            connection.execute(
                "INSERT INTO evidence VALUES(?,?,?,?)",
                (digest, format_name, raw, event_digest),
            )
            connection.executemany(
                "INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?)",
                [(digest, event.line, *event.values) for event in events],
            )
            append(
                connection,
                {
                    "action": "collect",
                    "operator": operator,
                    "utc": timestamp,
                    "evidence": digest,
                    "source_code": source,
                    "format": format_name,
                    "bytes": len(raw),
                    "events_digest": event_digest,
                    "event_count": len(events),
                },
            )
        return digest

    def record(self, digest: str, action: str, operator: str, timestamp: str) -> None:
        """Record review/handoff assertions, not verified human identity or physical possession."""
        operator, timestamp = token(operator), utc(timestamp)
        if (
            action not in {"review", "handoff"}
            or not isinstance(digest, str)
            or not DIGEST.fullmatch(digest)
        ):
            raise EvidenceError("invalid_custody_request")
        with self.connection(write=True) as connection:
            self._verify(connection)
            if not connection.execute(
                "SELECT 1 FROM evidence WHERE digest=?", (digest,)
            ).fetchone():
                raise EvidenceError("evidence_not_found")
            append(
                connection,
                {
                    "action": action,
                    "operator": operator,
                    "utc": timestamp,
                    "evidence": digest,
                },
            )

    def checkpoint(self, path: Path) -> None:
        """Save a new private prefix pin; move a copy to independently protected storage yourself."""
        verified = self.verify()
        write_new(
            path,
            canonical(
                {key: verified[key] for key in ("schema", "case_id", "seq", "head")}
            )
            + b"\n",
        )

    def timeline(
        self,
        connection: sqlite3.Connection,
        *,
        kind: str | None = None,
        start: str | None = None,
        end: str | None = None,
        limit: int = 1000,
        cursor: tuple[str, str, int] | None = None,
    ) -> tuple[list[tuple[Any, ...]], int, bool]:
        """Read private rows in (UTC,digest,line) order with parameterized filters/keyset cursor."""
        if (
            type(limit) is not int
            or not 1 <= limit <= 1000
            or kind is not None
            and kind not in KINDS
        ):
            raise EvidenceError("timeline_filter")
        start, end = (
            utc(start) if start is not None else None,
            utc(end) if end is not None else None,
        )
        if start and end and start >= end:
            raise EvidenceError("timeline_range")
        clauses = ["1=1"]
        parameters: list[str | int] = []
        for clause, value in (("kind=?", kind), ("utc>=?", start), ("utc<?", end)):
            if value is not None:
                clauses.append(clause)
                parameters.append(value)
        where = " AND ".join(clauses)
        count = connection.execute(
            "SELECT count(*) FROM events WHERE " + where, parameters
        ).fetchone()[0]
        if cursor is not None:
            if (
                len(cursor) != 3
                or cursor[0] != utc(cursor[0])
                or not DIGEST.fullmatch(cursor[1])
                or type(cursor[2]) is not int
                or cursor[2] < 1
            ):
                raise EvidenceError("timeline_cursor")
            where += " AND (utc,evidence_digest,line)>(?,?,?)"
            parameters.extend(cursor)
        rows = connection.execute(
            "SELECT utc,evidence_digest,line,kind,actor,asset FROM events WHERE "
            + where
            + " ORDER BY utc,evidence_digest,line LIMIT ?",
            [*parameters, limit + 1],
        ).fetchall()
        return rows[:limit], count, len(rows) > limit
