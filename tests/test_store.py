"""Actual SQLite atomicity, tamper, checkpoint, concurrency and timeline integration. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: collected — line 141
# parameter: case — line 141
# parameter: sample — line 141
# definition: pin — line 146
# parameter: case — line 146
# variable: result — line 148
# variable: name — line 149
# definition: test_collect_and_dedupe — line 152
# parameter: case — line 152
# parameter: sample — line 152
# variable: original — line 154
# variable: digest — line 155
# variable: before — line 157
# variable: connection — line 166
# definition: test_format_conflict — line 170
# parameter: case — line 170
# parameter: sample — line 170
# definition: test_malformed_atomic — line 178
# parameter: case — line 178
# parameter: sample — line 178
# variable: before — line 180
# definition: test_transaction_rollback — line 187
# parameter: case — line 187
# variable: before — line 189
# variable: connection — line 190
# definition: test_checkpoint_prefix_extensions — line 197
# parameter: action — line 197
# parameter: case — line 197
# parameter: sample — line 197
# parameter: tmp_path — line 197
# variable: digest — line 199
# variable: checkpoint — line 200
# definition: test_bad_checkpoint — line 224
# parameter: case — line 224
# parameter: changes — line 224
# variable: checkpoint — line 226
# definition: test_bad_pin_shape — line 232
# parameter: case — line 232
# parameter: checkpoint — line 232
# definition: test_immutable_triggers — line 251
# parameter: case — line 251
# parameter: sample — line 251
# parameter: sql — line 251
# variable: before — line 254
# variable: connection — line 257
# definition: test_tamper_detection — line 278
# parameter: case — line 278
# parameter: mutation — line 278
# parameter: sample — line 278
# variable: digest — line 280
# variable: checkpoint — line 281
# variable: connection — line 282
# variable: connection — line 312
# definition: test_concurrent_idempotency — line 333
# parameter: case — line 333
# parameter: sample — line 333
# variable: pool — line 335
# parameter: _ — line 336
# variable: digests — line 336
# definition: test_concurrent_handoffs — line 341
# parameter: case — line 341
# parameter: sample — line 341
# variable: digest — line 343
# variable: pool — line 344
# parameter: number — line 347
# definition: test_timeline_order_filters_and_keyset — line 354
# parameter: case — line 354
# parameter: sample — line 354
# variable: row — line 359
# variable: connection — line 368
# variable: count — line 369
# variable: more — line 369
# variable: rows — line 369
# variable: cursor — line 371
# variable: _ — line 372
# variable: more — line 372
# variable: page — line 372
# variable: row — line 373
# variable: _ — line 374
# variable: count — line 374
# variable: rows — line 374
# variable: plan — line 379
# variable: row — line 383
# definition: test_bad_timeline — line 401
# parameter: arguments — line 401
# parameter: case — line 401
# variable: connection — line 403
# definition: test_bad_record — line 410
# parameter: action — line 410
# parameter: case — line 410
# parameter: digest — line 410
# definition: test_collection_limit_rollback — line 416
# parameter: case — line 416
# parameter: monkeypatch — line 416
# parameter: sample — line 416
# variable: before — line 418
# variable: constant — line 419
# variable: patch — line 420
# definition: test_case_open_boundary — line 429
# parameter: tmp_path — line 429
# definition: test_valid_hash_invalid_semantics — line 446
# parameter: case — line 446
# parameter: payload — line 446
# variable: connection — line 448
# definition: test_wrong_collection_commitment — line 457
# parameter: case — line 457
# parameter: sample — line 457
# variable: raw — line 459
# variable: events_digest — line 462
# variable: record — line 463
# variable: connection — line 465
# definition: test_canonical_custody_time — line 488
# parameter: case — line 488
# variable: connection — line 490
# definition: test_reverify_case_limit — line 504
# parameter: case — line 504
# parameter: monkeypatch — line 504
# parameter: sample — line 504
# definition: test_empty_custody — line 512
# parameter: case — line 512
# variable: connection — line 514
# definition: test_invalid_metadata_value — line 521
# parameter: case — line 521
# variable: connection — line 523
# END CODE MAP

import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing

import pytest
from conftest import NOW, event

from irkit.contracts import EvidenceError, canonical, sha
from irkit.store import Case, append


def collected(case, sample):
    """Collect one synthetic source into the supplied isolated case and return its private digest."""
    return case.collect(sample, "jsonl", "analyst-a", "host-demo", NOW)


def pin(case):
    """Create a separately retained in-memory pin from independently returned private state."""
    result = case.verify()
    return {name: result[name] for name in ("schema", "case_id", "seq", "head")}


def test_collect_and_dedupe(case, sample):
    """Bytes/events/provenance commit together; identical retries do not append duplicate custody."""
    original = sample.read_bytes()
    digest = collected(case, sample)
    assert digest == sha(original)
    before = case.verify()
    assert (
        before["files"] == 1
        and before["events"] == 1
        and before["bytes"] == len(original)
        and before["seq"] == 2
    )
    assert collected(case, sample) == digest and case.verify() == before
    assert sample.read_bytes() == original
    with case.connection() as connection:
        assert connection.execute("SELECT raw FROM evidence").fetchone()[0] == original


def test_format_conflict(case, sample):
    """Identical bytes cannot silently reinterpret an earlier opaque collection as events."""
    case.collect(sample, "opaque", "analyst-a", "host-demo", NOW)
    with pytest.raises(EvidenceError, match="format_conflict"):
        collected(case, sample)
    assert case.verify()["events"] == 0


def test_malformed_atomic(case, sample):
    """A bad later row leaves neither a partial event batch nor an evidence/provenance row."""
    before = case.verify()
    sample.write_bytes(sample.read_bytes() + b'{"private":"PRIVATE-SENTINEL"}')
    with pytest.raises(EvidenceError):
        collected(case, sample)
    assert case.verify() == before


def test_transaction_rollback(case):
    """A real injected exception rolls back the SQLite custody insertion on the same connection."""
    before = case.verify()
    with pytest.raises(RuntimeError), case.connection(write=True) as connection:
        append(connection, {"action": "not-committed"})
        raise RuntimeError("synthetic failure")
    assert case.verify() == before


@pytest.mark.parametrize("action", ["review", "handoff"])
def test_checkpoint_prefix_extensions(case, sample, tmp_path, action):
    """Old pins remain valid after legitimate append-only extensions; file pin cannot be overwritten."""
    digest = collected(case, sample)
    checkpoint = pin(case)
    case.checkpoint(tmp_path / "pin.json")
    assert json.loads((tmp_path / "pin.json").read_text()) == checkpoint
    case.record(digest, action, "analyst-b", NOW)
    assert case.verify(checkpoint)["anchored"] and case.verify()["seq"] == 3
    with pytest.raises(FileExistsError):
        case.checkpoint(tmp_path / "pin.json")


@pytest.mark.parametrize(
    "changes",
    [
        {"schema": True},
        {"schema": 2},
        {"case_id": "wrong"},
        {"seq": True},
        {"seq": 0},
        {"seq": 99},
        {"head": "f" * 64},
        {"head": 1},
        {"head": "bad"},
        {"extra": "PRIVATE-SENTINEL"},
    ],
)
def test_bad_checkpoint(case, changes):
    """Invalid/cross-case/truncated/tampered checkpoint types or values fail closed."""
    checkpoint = {**pin(case), **changes}
    with pytest.raises(EvidenceError, match="checkpoint_mismatch"):
        case.verify(checkpoint)


@pytest.mark.parametrize("checkpoint", [[], "PRIVATE-SENTINEL", {}, 1])
def test_bad_pin_shape(case, checkpoint):
    """A pin must be exactly the schema, case ID, sequence and hash object."""
    with pytest.raises(EvidenceError):
        case.verify(checkpoint)


@pytest.mark.parametrize(
    "sql",
    [
        "UPDATE evidence SET raw=x'00'",
        "DELETE FROM evidence",
        "UPDATE events SET message='changed'",
        "DELETE FROM events",
        "UPDATE custody SET head='bad'",
        "DELETE FROM custody",
        "UPDATE metadata SET case_id='changed'",
        "DELETE FROM metadata",
    ],
)
def test_immutable_triggers(case, sample, sql):
    """Real SQL update/delete triggers enforce immutability even outside the application methods."""
    collected(case, sample)
    before = case.verify()
    with (
        pytest.raises(sqlite3.IntegrityError),
        case.connection(write=True) as connection,
    ):
        connection.execute(sql)
    assert case.verify() == before


@pytest.mark.parametrize(
    "mutation",
    [
        "raw",
        "events",
        "custody",
        "metadata",
        "schema",
        "version",
        "untracked",
        "foreign_key",
        "deleted_tail",
        "missing_table",
    ],
)
def test_tamper_detection(case, sample, mutation):
    """Bypass triggers only in disposable test data; verify detects each independently altered boundary."""
    digest = collected(case, sample)
    checkpoint = pin(case)
    with case.connection(write=True) as connection:
        if mutation == "raw":
            connection.execute("DROP TRIGGER evidence_no_update")
            connection.execute("UPDATE evidence SET raw=x'00'")
        elif mutation == "events":
            connection.execute("DROP TRIGGER events_no_update")
            connection.execute("UPDATE events SET message='PRIVATE-SENTINEL-CHANGED'")
        elif mutation == "custody":
            connection.execute("DROP TRIGGER custody_no_update")
            connection.execute("UPDATE custody SET payload='{}' WHERE seq=2")
        elif mutation == "metadata":
            connection.execute("INSERT INTO metadata SELECT * FROM metadata")
        elif mutation == "schema":
            connection.execute("CREATE TABLE surprise(x TEXT)")
        elif mutation == "version":
            connection.execute("PRAGMA user_version=2")
        elif mutation == "untracked":
            connection.execute(
                "INSERT INTO evidence VALUES(?,?,?,?)",
                (sha(b"opaque"), "opaque", b"opaque", sha(canonical([]))),
            )
        elif mutation == "foreign_key":
            # Deferred FK violation cannot be committed; test using a raw connection instead below.
            pass
        elif mutation == "deleted_tail":
            connection.execute("DROP TRIGGER custody_no_delete")
            connection.execute("DELETE FROM custody WHERE seq=2")
        else:
            connection.execute("DROP TABLE events")
    if mutation == "foreign_key":
        with closing(sqlite3.connect(case.database)) as connection:
            connection.execute(
                "INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    "f" * 64,
                    99,
                    "fake",
                    "2026-10-10T00:00:00.000000Z",
                    NOW,
                    "alert",
                    "x",
                    "y",
                    "z",
                ),
            )
            connection.commit()
    with pytest.raises(EvidenceError):
        case.verify(checkpoint)
    assert digest


def test_concurrent_idempotency(case, sample):
    """Eight actual concurrent connections serialize ingestion without duplicate batches or broken chain."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        digests = list(pool.map(lambda _: collected(case, sample), range(8)))
    assert len(set(digests)) == 1
    assert case.verify()["seq"] == 2


def test_concurrent_handoffs(case, sample):
    """Eight custody appends use immediate transactions so every sequence/hash predecessor is unique."""
    digest = collected(case, sample)
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(
            pool.map(
                lambda number: case.record(digest, "review", f"analyst-{number}", NOW),
                range(8),
            )
        )
    assert case.verify()["seq"] == 10


def test_timeline_order_filters_and_keyset(case, sample):
    """UTC ordering/ties, exclusive end, indexed filters and a cursor produce no duplicated page rows."""
    sample.write_text(
        "\n".join(
            json.dumps(row)
            for row in (
                event("late", "2026-10-10T16:01:00Z"),
                event("early", "2026-10-10T09:00:00-07:00"),
                event("tie", "2026-10-10T18:00:00+02:00", kind="alert"),
            )
        ),
        encoding="utf-8",
    )
    collected(case, sample)
    with case.connection() as connection:
        rows, count, more = case.timeline(connection, limit=1)
        assert count == 3 and more and rows[0][2] == 2
        cursor = rows[0][:3]
        page, _, more = case.timeline(connection, cursor=cursor, limit=2)
        assert [row[2] for row in page] == [3, 1] and not more
        rows, count, _ = case.timeline(
            connection, start="2026-10-10T16:00:00Z", end="2026-10-10T16:01:00Z"
        )
        assert count == 2 and len(rows) == 2
        assert case.timeline(connection, kind="alert")[1] == 1
        plan = connection.execute(
            "EXPLAIN QUERY PLAN SELECT * FROM events WHERE kind=? ORDER BY utc,evidence_digest,line LIMIT 2",
            ("alert",),
        ).fetchall()
        assert any("kind_timeline" in row[-1] for row in plan)


@pytest.mark.parametrize(
    "arguments",
    [
        {"limit": True},
        {"limit": 0},
        {"limit": 1001},
        {"kind": "raw"},
        {"start": NOW, "end": NOW},
        {"cursor": (NOW, "f" * 64, 1)},
        {"cursor": ("2026-10-10T00:00:00.000000Z", "bad", 1)},
        {"cursor": ("2026-10-10T00:00:00.000000Z", "f" * 64, 0)},
        {"cursor": ("2026-10-10T00:00:00.000000Z", "f" * 64, True)},
        {"cursor": ("bad",)},
    ],
)
def test_bad_timeline(case, arguments):
    """Reject invalid pagination/ranges/types; never interpolate filter values into SQL."""
    with case.connection() as connection, pytest.raises(EvidenceError):
        case.timeline(connection, **arguments)


@pytest.mark.parametrize(
    "action,digest", [("erase", "f" * 64), ("review", "../bad"), ("review", "f" * 64)]
)
def test_bad_record(case, action, digest):
    """Unknown actions, malformed IDs and absent evidence cannot create false custody entries."""
    with pytest.raises(EvidenceError):
        case.record(digest, action, "analyst-a", NOW)


def test_collection_limit_rollback(case, sample, monkeypatch):
    """Case byte/event/custody caps reject before an incomplete batch becomes visible."""
    before = case.verify()
    for constant in ("MAX_CASE", "MAX_EVENTS", "MAX_CUSTODY"):
        with monkeypatch.context() as patch:
            patch.setattr(
                "irkit.store." + constant, 1 if constant == "MAX_CUSTODY" else 0
            )
            with pytest.raises(EvidenceError):
                collected(case, sample)
        assert case.verify() == before


def test_case_open_boundary(tmp_path):
    """An arbitrary directory or absent database cannot become a case through opening."""
    with pytest.raises(EvidenceError):
        Case(tmp_path)
    with pytest.raises(FileExistsError):
        Case.create(tmp_path, "analyst-a", NOW)


@pytest.mark.parametrize(
    "payload",
    [
        {"action": "unknown"},
        {"action": "collect", "evidence": "f" * 64},
        {"action": "review", "evidence": "f" * 64},
        {"action": "handoff", "evidence": "f" * 64, "extra": "hidden"},
    ],
)
def test_valid_hash_invalid_semantics(case, payload):
    """Correctly hashed but semantically invalid provenance is rejected, not mistaken for genuine custody."""
    with case.connection(write=True) as connection:
        append(
            connection,
            {"operator": "analyst-a", "utc": "2026-10-10T16:03:00.000000Z", **payload},
        )
    with pytest.raises(EvidenceError):
        case.verify()


def test_wrong_collection_commitment(case, sample):
    """A correctly linked collection with wrong event metadata cannot authorize an untracked BLOB."""
    raw = sample.read_bytes()
    from irkit.parsing import parse

    events_digest = sha(
        canonical([record.committed() for record in parse(raw, "jsonl")])
    )
    with case.connection(write=True) as connection:
        connection.execute(
            "INSERT INTO evidence VALUES(?,?,?,?)",
            (sha(raw), "opaque", raw, sha(canonical([]))),
        )
        append(
            connection,
            {
                "action": "collect",
                "operator": "analyst-a",
                "utc": "2026-10-10T16:03:00.000000Z",
                "evidence": sha(raw),
                "source_code": "host-demo",
                "format": "jsonl",
                "bytes": len(raw),
                "event_count": 1,
                "events_digest": events_digest,
            },
        )
    with pytest.raises(EvidenceError, match="collection_integrity"):
        case.verify()


def test_canonical_custody_time(case):
    """Custody must store canonical UTC even if an attacker supplies an otherwise equivalent offset."""
    with case.connection(write=True) as connection:
        append(
            connection,
            {
                "action": "review",
                "operator": "analyst-a",
                "utc": NOW,
                "evidence": "f" * 64,
            },
        )
    with pytest.raises(EvidenceError, match="custody_integrity"):
        case.verify()


def test_reverify_case_limit(case, sample, monkeypatch):
    """Integrity checking independently re-enforces total size and event caps on stored content."""
    collected(case, sample)
    monkeypatch.setattr("irkit.store.MAX_CASE", 1)
    with pytest.raises(EvidenceError, match="case_limits"):
        case.verify()


def test_empty_custody(case):
    """Deleting genesis by bypassing a trigger is detected before any false successful verification."""
    with case.connection(write=True) as connection:
        connection.execute("DROP TRIGGER custody_no_delete")
        connection.execute("DELETE FROM custody")
    with pytest.raises(EvidenceError, match="custody_limit"):
        case.verify()


def test_invalid_metadata_value(case):
    """A malformed case ID is rejected even when an administrator bypasses mutation controls."""
    with case.connection(write=True) as connection:
        connection.execute("DROP TRIGGER metadata_no_update")
        connection.execute("UPDATE metadata SET case_id='not-a-hex-uuid'")
    with pytest.raises(EvidenceError, match="metadata_integrity"):
        case.verify()
