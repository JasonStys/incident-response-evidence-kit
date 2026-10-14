# Runbook: authorized local evidence and reproducible demos

Created by Jason Stys. Help/contact: [GitHub](https://github.com/JasonStys), [LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/).

## Before collection

Obtain explicit authorization for the specific source, document collection authority/source/clock/operator-code mapping privately, and follow legal/organizational incident procedures. Use a trusted encrypted disk and appropriate directory ACLs. Close untrusted programs. Do not collect unrelated resumes, emails, private employer code or broad home folders. The CLI reads only the file you name; `--ack-authorized` is an acknowledgement, not independent proof.

Create a new parent directory yourself (`out` for fictional demo work). A new case cannot replace an existing folder. `python -m irkit --help` lists commands; each supports `--help`. Application runtime is Python 3.12+ standard library, no package installation beyond Python. Development tools require the hash-locked environment from README. Optional native hashing requires Rust 1.98.0 and the Cargo lock graph.

## Case lifecycle

1. `python -m irkit init out/case-one --operator analyst-a` creates a plaintext private database/genesis.
2. `python -m irkit collect out/case-one examples/access-review.jsonl --format jsonl --source access-demo --operator analyst-a --ack-authorized` preserves exact bytes and returns a **private** reference. Prefer source reference codes to names/IP/path display values; retain code mapping under your organization's controls.
3. `python -m irkit record out/case-one PRIVATE_DIGEST --action review --operator analyst-b` records a review assertion. `handoff` records another handling assertion; neither proves possession or identity.
4. `python -m irkit checkpoint out/case-one out/checkpoint-one.json` saves a prefix pin. Preserve a separately controlled copy **before** relying on it; never publish its IDs/hashes by default. Future pins must use new output names.
5. `python -m irkit verify out/case-one --checkpoint out/checkpoint-one.json` rechecks byte/event/provenance/schema integrity and the supplied prefix. Without a pin it reports `anchored=False`, not authenticated history.
6. `python -m irkit export out/case-one out/review-one --checkpoint out/checkpoint-one.json --start 2026-10-10T16:00:00Z --end 2026-10-10T16:03:00Z --limit 1000` creates JSON, CSV and inert HTML. Review all contents/recipient permissions before sharing; exact timestamps/patterns remain sensitive. Report does not contain private event messages.

Rust oracle: `cargo build --release --locked --manifest-path native/Cargo.toml`, then feed **bytes** to `native/target/release/evidence-digest` via stdin from a trusted shell/Python binary reader. Windows PowerShell string pipelines are not byte-faithful; use `python scripts/native_check.py` for portable equivalence validation, not `Get-Content | ...` on binary evidence. The binary prints count+SHA256 and reads at most 20 MiB+1 byte; keep real digest output private. It does not validate SQLite custody or parse events.

## Troubleshooting and failures

- Existing output: choose a new directory/file; nothing is overwritten or silently deleted. A failed initialization/export may leave a partial directory; inspect it privately and use a new name. No automated cleanup is provided.
- Timestamp/field/schema rejection: original source stays unchanged; correct an **authorized working copy** with an explicit transformation record, never rewrite original evidence to make it fit. `opaque` can preserve unsupported data without pretending to normalize it.
- SQLite lock timeout: stop concurrent mutation attempts, wait for the authorized writer to finish and retry explicitly. No unbounded retries/background locks. Read filters are parameterized; do not edit SQL/database rows.
- Integrity/checkpoint mismatch: stop export/mutations; preserve all copies, checkpoint and database; investigate under your procedures. Do not regenerate pins to silence a failure. Unknown format or event kind requires a reviewed adapter/schema change, not automatic guessing.
- Permissions/setup: ensure a trusted writable working directory. Windows venv/temp-folder policy may require an approved workspace-local temp directory; do not disable security software or modify host-wide permissions. Logs are never sent to a server.
- Rust/dev audit failures: update reviewed pinned versions and tests; never suppress advisories/skip tests or widen CI tokens to obtain a green badge.

## Backup and release rollback

Quiesce all writers; preserve the **entire private case directory** plus separately controlled checkpoint copies and code/operator mapping. Use your organization's encrypted backup procedure. Verify a restored working copy against the original independently retained pin before resuming. This project does not automate verified encrypted backup or guarantee crash-snapshot consistency; don't copy an actively mutating SQLite database casually.

Source version rollback: clone a reviewed earlier commit into a new workspace, run full checks and verify a duplicate case against its saved checkpoint. There is only schema1; unsupported version fails rather than silently migrate. Never roll back/delete a case history to match a code version.

## CI storage preference

Before workflow work inspect live Actions artifact/cache usage and available billing meter; distinguish accumulated billing from current bytes. Workflows in this repo deliberately upload no artifacts and enable no Actions cache. Account cleanup always needs fresh Jason approval, verified private archives, explicit unavailable notices and preservation of newest/active runs. No new cleanup, retention-policy, Packages or billing change is authorized by creating this repo.
