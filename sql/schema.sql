-- Jason Stys: transactional private BLOB evidence, ordered provenance and indexed immutable events.
-- BEGIN CODE MAP (generated; python scripts/code_map.py)
-- column: case_id — line 28
-- column: pseudonym_key — line 28
-- table: metadata — line 28
-- table: evidence — line 29
-- column: digest — line 30
-- column: format — line 31
-- column: raw — line 32
-- column: events_digest — line 33
-- table: events — line 35
-- column: evidence_digest — line 36
-- column: line — line 37
-- column: event_id — line 38
-- column: utc — line 39
-- column: source_time — line 40
-- column: kind — line 41
-- column: actor — line 42
-- column: asset — line 43
-- column: message — line 44
-- table: custody — line 50
-- column: seq — line 51
-- column: payload — line 52
-- column: previous — line 53
-- column: head — line 54
-- END CODE MAP
PRAGMA foreign_keys = ON;
CREATE TABLE metadata (case_id TEXT NOT NULL, pseudonym_key BLOB NOT NULL CHECK(length(pseudonym_key)=32));
CREATE TABLE evidence (
    digest TEXT PRIMARY KEY CHECK(length(digest)=64),
    format TEXT NOT NULL CHECK(format IN ('jsonl','csv','opaque')),
    raw BLOB NOT NULL CHECK(length(raw)<=20971520),
    events_digest TEXT NOT NULL CHECK(length(events_digest)=64)
) STRICT;
CREATE TABLE events (
    evidence_digest TEXT NOT NULL REFERENCES evidence(digest),
    line INTEGER NOT NULL CHECK(line>0),
    event_id TEXT NOT NULL,
    utc TEXT NOT NULL,
    source_time TEXT NOT NULL,
    kind TEXT NOT NULL,
    actor TEXT NOT NULL,
    asset TEXT NOT NULL,
    message TEXT NOT NULL,
    PRIMARY KEY(evidence_digest,line),
    UNIQUE(evidence_digest,event_id)
) STRICT;
CREATE INDEX timeline ON events(utc,evidence_digest,line);
CREATE INDEX kind_timeline ON events(kind,utc,evidence_digest,line);
CREATE TABLE custody (
    seq INTEGER PRIMARY KEY CHECK(seq>0),
    payload TEXT NOT NULL,
    previous TEXT NOT NULL CHECK(length(previous)=64),
    head TEXT NOT NULL CHECK(length(head)=64)
) STRICT;
CREATE TRIGGER evidence_no_update BEFORE UPDATE ON evidence BEGIN SELECT RAISE(ABORT,'immutable_evidence'); END;
CREATE TRIGGER evidence_no_delete BEFORE DELETE ON evidence BEGIN SELECT RAISE(ABORT,'immutable_evidence'); END;
CREATE TRIGGER events_no_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT,'immutable_events'); END;
CREATE TRIGGER events_no_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT,'immutable_events'); END;
CREATE TRIGGER custody_no_update BEFORE UPDATE ON custody BEGIN SELECT RAISE(ABORT,'immutable_custody'); END;
CREATE TRIGGER custody_no_delete BEFORE DELETE ON custody BEGIN SELECT RAISE(ABORT,'immutable_custody'); END;
CREATE TRIGGER metadata_no_update BEFORE UPDATE ON metadata BEGIN SELECT RAISE(ABORT,'immutable_metadata'); END;
CREATE TRIGGER metadata_no_delete BEFORE DELETE ON metadata BEGIN SELECT RAISE(ABORT,'immutable_metadata'); END;
