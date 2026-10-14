# Incident Response Evidence Kit

[![Validate](https://github.com/JasonStys/incident-response-evidence-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonStys/incident-response-evidence-kit/actions/workflows/ci.yml)
[![CodeQL](https://github.com/JasonStys/incident-response-evidence-kit/actions/workflows/codeql.yml/badge.svg)](https://github.com/JasonStys/incident-response-evidence-kit/actions/workflows/codeql.yml)

Created by **Jason Stys** · [GitHub/contact](https://github.com/JasonStys) · [LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/)

A defensive, local-only investigation toolkit: preserve authorized original file bytes, normalize events without guessing time zones, verify collection provenance, and create a deliberately minimized review timeline. Unlike a generic incident dashboard, the important question here is **whether a timeline can still be traced to the bytes that were collected**. All included examples are fictional. No host scanning, remote collection, uploaded evidence, AI attribution or live threat interaction is performed.

This is an educational portfolio tool, **not a certified forensic product, proof of legal admissibility, NIST compliance or protection from the host administrator**. Case databases are plaintext and contain sensitive original data; use a trusted encrypted disk and appropriate OS access controls. An internally consistent hash chain can be rewritten by an administrator. An independently protected checkpoint is needed to detect rewriting/truncation of the anchored prefix. Pseudonymized reports are not anonymized.

## Features and major functions

| Feature | Main implementation and behavior |
| --- | --- |
| Exact acquisition | `read_file`: regular-file descriptor, size cap, symlink/reparse rejection, before/after stability checks; source remains unchanged. |
| Strict normalization | `Event.parse` / `parse` / `utc`: JSONL and CSV adapters, duplicate-key/ID rejection, exact schemas, known numeric offsets, microsecond UTC, original source timestamp retained privately. |
| Private immutable storage | `Case.create` / `Case.collect`: real SQLite transactions commit original BLOB, normalized rows and custody entry together; repeat same bytes/format is idempotent. |
| Custody assertions | `Case.record`: bounded review/handoff entries with operator/source reference codes; append-only hash-linked sequence and mutation-blocking SQL triggers. |
| Integrity / checkpoints | `Case.verify` / `checkpoint`: rehash raw BLOBs, independently reparse and compare events, check schema/provenance, optionally compare an externally retained prefix pin. |
| Investigation timeline | `Case.timeline`: stable `(UTC,evidence digest,source line)` ordering, kind/time filters and indexed keyset pagination. Source clocks are not treated as ground truth. |
| Minimized reports | `export`: consistent verified snapshot, HMAC domain-separated case-specific pseudonyms, no raw messages/paths/original identities/hashes, bounded JSON/CSV/inert HTML. |
| Independent native oracle | Rust `digest_reader`: 8KiB streaming buffer, established RustCrypto SHA256, exact 20MiB cap; cross-language checks against Python/OpenSSL-backed hashlib and fixed vectors. |
| Operational evidence | Real CLI/demo, atomicity/concurrency/tamper/property/privacy tests, measured benchmark, pinned dependency/scanner/Actions gates. No Actions artifact uploads or caches. |

## First successful run

Python3.12+ and Git are required; the application runtime uses only the Python standard library. From a fresh clone:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-dev.lock
.venv\Scripts\python.exe -m scripts.demo
```

On Linux/macOS replace `.venv\Scripts\python.exe` with `.venv/bin/python`. Open `out/demo/report/report.html` as a local file. This runs actual SQLite collection of two fictional sources, five events and five custody entries, then verifies a saved checkpoint and produces three minimized review formats. It does not simulate the database or claim that a compromised machine was examined. It refuses to overwrite `out/demo`; use the manual CLI with a new directory for repeat work. The optional Rust tool is not needed for the Python application.

Manual workflow (create the parent `out` once if it does not exist):

```powershell
python -m irkit init out/new-case --operator analyst-a
python -m irkit collect out/new-case examples/access-review.jsonl --format jsonl --source access-demo --operator analyst-a --ack-authorized
python -m irkit checkpoint out/new-case out/checkpoint-1.json
python -m irkit verify out/new-case --checkpoint out/checkpoint-1.json
python -m irkit export out/new-case out/review-copy --checkpoint out/checkpoint-1.json --kind auth_failure --limit 100
```

`collect` prints a **private** evidence reference for `record CASE DIGEST --action review|handoff --operator analyst-b`. Keep that console output in authorized records. Copy a checkpoint to independently access-controlled storage; an automatically saved same-disk file is not independent authentication. Checkpoints expose case/root identifiers and stay private by default. Use `python -m irkit --help` or command-specific `--help`; detailed help, bounds, troubleshooting and backup procedures are in the [runbook](docs/runbook.md).

## Architecture and performance boundaries

```text
explicit authorized file → stable bounded bytes → strict CSV/JSONL adapter
                                  ↓                     ↓
                           original SQLite BLOB ← atomic → events
                                  └──── custody SHA256 chain ────┐
                                                               ↓
independent prefix checkpoint → verification/reparse → indexed timeline
                                                               ↓
                                     approved-field projection → local JSON/CSV/HTML
```

Python suits portable orchestration/schema/CLI work; SQL makes transaction, uniqueness and query ordering explicit; Rust provides a separately compiled bounded streaming digest tool; Bash makes CI fail-fast; HTML presents escaped evidence without active scripts. No invented cryptography or unnecessary service dependencies. Important complexity and storage limits are in [architecture](docs/architecture.md) and [contracts](docs/contracts.md). Bounded in-memory import is intentional; this is not a disk-image-scale collector. Keyset querying is indexed, but exporting deliberately revalidates the **whole bounded case**, so end-to-end report time includes that work.

## Verification and documentation

See [testing](docs/testing.md), [measured validation](docs/reports/validation.md), [threat model](docs/threat-model.md), [research](docs/research.md) and [contribution rules](CONTRIBUTING.md). Tests fail on warnings, malformed inputs, insufficient branch/statement coverage, stale symbol maps or missing file purposes. Raw evidence is never checked in or uploaded by CI. Public selected demo reports are from fictional data, not an investigation. CI status badges are live; acceptance records bind to specific completed source commits.

Every authored code file describes its purpose and has generated exact function/class/parameter/variable line locations. Function/class contracts document state and failure boundaries. Regenerate after formatting with `python scripts/code_map.py`; CI rejects stale maps. Shallow folders: `irkit/`, `sql/`, `native/`, `tests/`, `examples/`, `scripts/`, `docs/`, `.github/workflows/`.

## Complete file guide

<!-- BEGIN FILE GUIDE -->

| File | Purpose |
| --- | --- |
| [.gitattributes](.gitattributes) | Consistent LF source checkout across operating systems. |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | Jason Stys: native OS/property/integrity tests, cross-language digests and zero-storage security gates. |
| [.github/workflows/codeql.yml](.github/workflows/codeql.yml) | Jason Stys: security-extended Python analysis; no database archive upload. |
| [.gitignore](.gitignore) | Keep original evidence, private databases, checkpoints, tools and working data untracked. |
| [CHANGELOG.md](CHANGELOG.md) | Changelog. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution and maintenance. |
| [LICENSE](LICENSE) | MIT terms for authored source; upstream tools retain their licenses. |
| [README.md](README.md) | Incident Response Evidence Kit. |
| [SECURITY.md](SECURITY.md) | Security policy. |
| [docs/architecture.md](docs/architecture.md) | ADR-001: private transactional evidence with independent prefix checkpoints. |
| [docs/contracts.md](docs/contracts.md) | Formats, privacy and integrity contracts. |
| [docs/reports/validation.md](docs/reports/validation.md) | Measured validation and release review. |
| [docs/research.md](docs/research.md) | Primary-source research and design rationale. |
| [docs/runbook.md](docs/runbook.md) | Runbook: authorized local evidence and reproducible demos. |
| [docs/testing.md](docs/testing.md) | Test strategy and reproducible verification. |
| [docs/threat-model.md](docs/threat-model.md) | Threat model and deliberate limits. |
| [examples/access-review.jsonl](examples/access-review.jsonl) | Fictional access events with mixed offsets and unsorted records, no real accounts. |
| [examples/service-change.csv](examples/service-change.csv) | Fictional quoted service-change and alert CSV records, no real organizations. |
| [irkit/\_\_init\_\_.py](irkit/__init__.py) | Local incident evidence contracts by Jason Stys; no import-time I/O or network activity. |
| [irkit/\_\_main\_\_.py](irkit/__main__.py) | Local-only evidence CLI with explicit authorization and safe error output. Created by Jason Stys. |
| [irkit/contracts.py](irkit/contracts.py) | Strict schemas, safe errors and microsecond UTC normalization. Created by Jason Stys. |
| [irkit/files.py](irkit/files.py) | Bounded regular-file acquisition and exclusive output in trusted directories. Jason Stys. |
| [irkit/parsing.py](irkit/parsing.py) | Strict bounded JSONL/CSV event adapters; binary evidence is retained opaquely. Jason Stys. |
| [irkit/report.py](irkit/report.py) | Allowlisted pseudonymized JSON/CSV/inert HTML; raw messages never enter exports. Jason Stys. |
| [irkit/store.py](irkit/store.py) | Transactional private evidence, anchored custody checks and stable keyset timelines. Jason Stys. |
| [native/Cargo.lock](native/Cargo.lock) | Complete checksum-locked Rust dependency graph; no private input. |
| [native/Cargo.toml](native/Cargo.toml) | Independent Rust bounded streaming SHA256 CLI and exact RustCrypto input. |
| [native/src/main.rs](native/src/main.rs) | Native safe stdin hashing, known-vector/boundary/I/O/chunk tests and no input echo. |
| [pyproject.toml](pyproject.toml) | Strict lint/type/test/statement-and-branch coverage configuration. |
| [requirements-dev.in](requirements-dev.in) | Exact portable development tool inputs. |
| [requirements-dev.lock](requirements-dev.lock) | Complete hash-locked portable development graph. |
| [scripts/\_\_init\_\_.py](scripts/__init__.py) | Explicit local validation/demo tools by Jason Stys; importing tools performs no I/O. |
| [scripts/benchmark.py](scripts/benchmark.py) | Measure bounded synthetic parsing/SQLite collection/reverification; no speedup or SLA claim. Jason Stys. |
| [scripts/code\_map.py](scripts/code_map.py) | Generate/check exact Python, SQL, shell and YAML symbol positions. Created by Jason Stys. |
| [scripts/demo.py](scripts/demo.py) | Run actual synthetic collection, handoff, checkpoint and redacted reporting. Created by Jason Stys. |
| [scripts/file\_guide.py](scripts/file_guide.py) | Maintain a complete tracked-file README purpose inventory; unknown file types fail closed. Created by Jason Stys. |
| [scripts/native\_check.py](scripts/native_check.py) | Cross-language SHA256 and actual CLI rejection oracle, only against this built binary. Jason Stys. |
| [scripts/scanners.py](scripts/scanners.py) | Install only hash-pinned official Linux scanner binaries. Created by Jason Stys. |
| [scripts/validate.sh](scripts/validate.sh) | Jason Stys: fail-fast portable tests, source contracts and repository privacy invariants; no uploads. |
| [scripts/validate\_repo.py](scripts/validate_repo.py) | Gate tracked-file privacy, reviewed workflow/crypto bounds and internal documentation links. Jason Stys. |
| [sql/schema.sql](sql/schema.sql) | Jason Stys: transactional private BLOB evidence, ordered provenance and indexed immutable events. |
| [tests/conftest.py](tests/conftest.py) | Disposable synthetic evidence fixtures; never read real accounts or host logs. Jason Stys. |
| [tests/test\_anchor.py](tests/test_anchor.py) | Prove the difference between internal consistency and an independently retained prefix. Jason Stys. |
| [tests/test\_contracts.py](tests/test_contracts.py) | UTC/schema/JSON/property validation with independent expected values. Created by Jason Stys. |
| [tests/test\_parsing.py](tests/test_parsing.py) | JSONL/CSV malformed, duplicate, multiline and bounded-input regression tests. Jason Stys. |
| [tests/test\_privacy\_cli.py](tests/test_privacy_cli.py) | Actual CLI, public projection, output safety and source-path contracts. Created by Jason Stys. |
| [tests/test\_store.py](tests/test_store.py) | Actual SQLite atomicity, tamper, checkpoint, concurrency and timeline integration. Jason Stys. |
| [tools.lock.json](tools.lock.json) | Exact official scanner release hashes and compiler version. |

<!-- END FILE GUIDE -->

## Safety, attribution and next steps

Use only evidence you are authorized to acquire. Do not run this against a shared/production directory or publish `out/`, databases, checkpoint files or original CLI references. Follow your organization's legal/retention/incident procedures and review every report before sharing. No automatic claims of compromise, attribution, guilt or employment suitability. Planned extensions (not implemented): signed external attestations, encrypted database integration, streaming disk-image collection, additional explicit parsers, authenticated multi-user case review and measured process-crash/power-loss testing.

Authored source is MIT, copyright Jason Stys. Dependency licenses remain their own. Bugs/help: [GitHub](https://github.com/JasonStys/incident-response-evidence-kit/issues); sensitive disclosures follow [SECURITY](SECURITY.md), never public evidence uploads.
