# Measured validation and release review

Created by Jason Stys. Accepted executable source: [2c7232cdb6e5a74b969be023512d1055b2ee39c6](https://github.com/JasonStys/incident-response-evidence-kit/commit/2c7232cdb6e5a74b969be023512d1055b2ee39c6).

## Completed acceptance

[Validate 38516662018](https://github.com/JasonStys/incident-response-evidence-kit/actions/runs/38516662018) completed successfully, updated 2026-10-14T05:29:58Z, with all eight validation jobs passed. [CodeQL 38516662108](https://github.com/JasonStys/incident-response-evidence-kit/actions/runs/38516662108) completed successfully, updated 2026-10-14T05:27:34Z; the open-alert API returned zero. Both bind to the executable source above. [ci.json](ci.json) is an immutable acceptance snapshot, not a claim to bind to the report commit containing it. Documentation publication reruns every gate; live README badges/Actions show current-main results.

| Executed check | Measured result |
| --- | --- |
| Python 3.12 / Ubuntu 24.04 | 153 passed, zero failures/skips, 99.67% combined statement+branch runtime coverage |
| Python 3.14 / Ubuntu 24.04 | 153 passed, zero failures/skips, 99.67% combined runtime coverage |
| Python 3.14 / Windows hosted runner | 153 passed, zero failures/skips, 99.67% combined runtime coverage |
| Python 3.14 / Intel macOS 15 | 153 passed, zero failures/skips, 99.67% combined runtime coverage |
| Rust 1.98.0 / all three OSes | rustfmt, Clippy with warnings denied, locked compiler/tests/release build; four native tests; 21 Python/binary digest matches and actual oversize exit2 |
| Actual SQLite demo / every Python lane | Two fictional sources, five events and five custody entries; retained checkpoint match, sorted minimized JSON/CSV/HTML |
| Linux Rust advisory gate | Passed cargo-audit 0.22.2 with warnings denied and no ignores |
| Python/scanner/workflow security | Complete hash-locked development graph has no known vulnerabilities; full-history Gitleaks, actual actionlint and ShellCheck pass |
| CodeQL Python security-extended | Passed, zero open alerts; not a claim of Rust CodeQL coverage |
| Local Windows / Python 3.14.6 | Same 153 tests; 444/445 statements and 157/158 branches covered, combined 99.668325%; no exclusions |

All authored `irkit/` runtime code is the Python coverage denominator; tooling scripts/SQL/Rust are not hidden inside this figure. SQL runs in actual integration tests, and Rust has independent known vectors/compiler/interop oracles. POSIX-specific real symlink/mode assertions execute on Linux/macOS; Windows exercises guards without elevated symlink privileges. Warning filters remain strict.

Tests demonstrate malformed-input atomic rejection, duplicate retries, real exception rollback, update/delete triggers, wrong schema/version/FK checks, raw/normalized/custody tampering, safe error handling, timezone precision/ties, keyset pagination and actual index selection. Eight separate concurrent connections serialize duplicate import and custody appends. Two regressions deliberately create **internally consistent** administrator rewrites/truncations: they pass unanchored verification, then fail against the original prefix checkpoint. This demonstrates the trust limit rather than mislabeling a plain chain as authenticated evidence.

## Public evidence and benchmark scope

[local.json](local.json) records completed local assertions/audits. [demo.json](demo.json), [demo.csv](demo.csv) and [demo.html](demo.html) are approved-field review projections from the actual supplied fictional sources. Original case databases, keys, checkpoint IDs, messages, private paths and raw investigation logs are **not** published.

[benchmark.json](benchmark.json) records five actual Windows/Python 3.14.6 repetitions of 1,000 synthetic events / 188,889 input bytes:

| Operation | Median |
| --- | ---: |
| Complete parse | 10.88 ms |
| File read + SQLite collection/commit + existing-genesis verification | 40.00 ms |
| Whole-case rehash/reparse/database/custody verification | 23.54 ms |

Peak traced Python allocation during a separate parse was 1,161,072 bytes. It is not process RSS, native SQLite memory or an end-to-end resource budget. Measurements exclude virtualenv/compiler setup and are informational, not an SLA, disk-image benchmark or comparative speedup claim. No platform-specific latency threshold was used to conceal failures.

Local cargo-audit completed after the tool was built into ignored workspace storage: eleven Cargo.lock packages, zero vulnerabilities/warnings, no ignored advisories. Advisory database commit `6aed84668c23d7f535077a9fe918bf1fa0f6a5bc`, last updated 2026-10-13T17:07:33+02:00. This records the queried advisory snapshot, not a perpetual vulnerability-free guarantee.

## Development findings corrected before acceptance

- Standard Windows ensurepip could not use the sandbox host temp directory. Process-scoped workspace-local temp storage allowed the installer to complete; no host security/ACL setting changed.
- RustCrypto 0.11 output lacks the older array LowerHex trait. Standard byte-hex formatting plus independent empty/abc vectors and cross-language checks corrected compatibility without inventing cryptography.
- A deliberately sabotaging test fixture assumed the SQLite context manager closed its connection. Python 3.14 ResourceWarning correctly failed the suite. Explicit closing/commit repaired the fixture; application connections already close in `finally`. Warnings remain errors.
- Review added escaped surrogate rejection before SQLite UTF8 encoding, escaped HTML scalar values and consistent-rewrite/truncation regressions. Original messages remain private and are never projected into reports.
- The audit tool input was corrected to registry-verified 0.22.2 before publication. An initial local tool build hit sandbox temp write restrictions; the workspace-targeted retry and actual advisory check passed. No vulnerability ignore or disabled gate was used.
- Local Windows incremental compilation could not hard-link its cache and used file copies instead; native tests/builds succeeded. Hosted Clippy/compiler lanes are independently green. No global cache/security settings changed.

The first public source Validate/CodeQL runs both passed; no historical public failure was deleted to obtain that result.

## Storage, author review and limits

Read-only account check before workflow work: live artifacts 8,419,929 bytes, separate caches 9,029,833,071 bytes, included storage billing meter 100%. Accrued billing is not current occupancy. This repo's actual artifact/cache counts are both zero. No additional run deletion, cache/Packages/billing setting change or local Docker repair occurred.

Author review checked strict input/UTF8/clock boundaries, byte/event/provenance coupling, transaction/connection lifetimes, concurrency/identity assumptions, private/public projection, escaped output, independent pin limitations, exact dependency/action/scanner pins, file inventory and symbol maps. No production forensic certification, encrypted vault, authenticated human custody, power-loss/crash-test qualification or public multi-user service is claimed. Follow the [threat model](../threat-model.md) and [runbook](../runbook.md) before any authorized non-demo use.
