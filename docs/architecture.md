# ADR-001: private transactional evidence with independent prefix checkpoints

Status: accepted · Date: 2026-10-14 · Author/decider: Jason Stys

## Context and constraints

Build operational evidence for defensive security and DevOps roles. Preserve original authorized bytes, normalize heterogeneous logs, connect each event to its source and catch corruption without exposing private investigation data. Run locally across Windows/Linux/macOS; no cloud account, Docker, telemetry or system-wide settings required. The included scope is small cases, not forensic disk images or a shared SaaS.

## Decision and alternatives

Use stdlib Python with SQLite original BLOB/event/custody rows in a single atomic write transaction. SQLite is maintained, inspectable and locally reproducible. Separate flat BLOB files plus database metadata were rejected: an interrupted update can orphan data or point metadata at an incomplete file. A remote object store/queue/service was rejected because it adds privacy/operational boundaries without a measured need. SQL triggers deter ordinary update/delete; application verification rehashes bytes, independently reparses rows and validates commitments, so triggers are not the sole integrity check.

Use established SHA256 for integrity and HMAC-SHA256 for domain-separated report pseudonyms. A plain hash chain is **not an authentication signature**. An independently retained `(case ID,sequence,head)` pin verifies an anchored prefix while allowing legitimate later appends. A privileged adversary can replace unanchored content or future suffixes; signed timestamps and protected external ledgers are deferred. The Rust SHA256 stdin tool is an independently compiled cross-language oracle, not a vault or replacement hash implementation.

## State and transaction boundaries

- New case: new private directory/database, reviewed schema, one metadata record and genesis commitment to case ID/key/schema. Initialization failure can leave an incomplete private directory; never silently overwrite or erase it.
- Collect: explicit stable file read and complete parse → `BEGIN IMMEDIATE` → verify existing case → dedupe or insert bytes/events/custody → commit. Any exception rolls back database changes. Source files are never changed.
- Record: verify existing case and referenced evidence, append one asserted review/handoff. Operator codes are assertions, not authenticated identities or physical possession.
- Verify/export: read-only consistent SQLite snapshot. Full raw hashing/reparse/custody check precedes projection. Export writes a new directory; if a later output write fails, partial files may remain for manual inspection, with no original data in them. This is not a multi-file transactional export.
- Every connection closes in `finally`; foreign keys are enabled, trusted schema disabled, extension loading never enabled, synchronous commits requested. Five-second lock timeout, no unbounded retry.

## Complexity and scale

Let B be source bytes, E events, C custody entries and P displayed rows. File read/hash and parse are O(B), with O(B+E) bounded Python allocation. JSON per-record validation is linear in bounded record length. Import uniqueness sets are expected O(E) time/O(E) space (hash-map worst cases may degrade). Verification is O(B_total+E_total+C) plus indexed per-source lookups; schema work is constant-sized. SQL index insert/query is roughly O(log E) per indexed row; keyset fetch is O(log E+P) when the matching index is used. Filter count scans matches (not O(1)). Full-case export includes verification; do not call the entire operation O(P).

Limits: 20MiB per file, 64MiB original bytes per case, 256 files, 50,000 events, 10,000 custody records, 16KiB physical source line, 4,096 message characters, 256 other field characters, 1,000 report rows. Database opening rejects files over256MiB. Rust uses8KiB buffer/O(B) work and reads only cap+1 bytes to reject oversize. These caps are guardrails, not a promise of a hard CPU/RSS budget against a malicious database administrator.

## Consequences and revisit conditions

Private BLOBs simplify consistent recovery/backup but duplicate raw/normalized data and are plaintext. Reverification before every mutation is deliberately expensive for integrity; it would need authenticated incremental verification for large cases. No raw timeline browser is provided: CLI exports minimize data by default, but precise times/patterns may still identify people. Revisit encryption, authenticated custody, crash-injection and per-user authorization before any production or multi-user deployment. No pending action is being portrayed as implemented.
