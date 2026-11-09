# Bookmark handoff workflow validation — 2026-11-09

Created by Jason Stys. Windows/Python3.14.6/Rust1.98.0. Runtime remains dependency-free; isolated test graph installed with hash enforcement. All evidence is fictional and locally owned.

- Full suite: **168 passed**, **99.71% combined statement/branch coverage**, unchanged95% minimum. New bookmark module has100% measured coverage.
- Actual CLI template/edit/selected-handoff workflow resolves exact original digest/line, rechecks checkpoint and current case, preserves database bytes and creates only minimized JSON/HTML. Independent tests cover unknown/duplicate/bool/missing line references, stale custody state, no/wrong checkpoint, altered schema, invalid tags/operator/note, source-reference privacy and immutable outputs. Raw notes/operator/digest/case-ID sentinels do not enter the handoff.
- Existing two-source demo: **2files /5events /5custody entries**, matched checkpoint and allowlisted reports. Demo/benchmark now accept an optional new `--output` destination; default behavior and overwrite refusal remain unchanged. Prior `out/demo` was preserved when repeat execution correctly refused it; validation used a fresh destination.
- Existing Rust locked build and **4 native tests** pass; **21 Python/Rust digest comparisons** and over20MiB rejection pass. Rust fmt/clippy warnings-as-errors passed; incremental caching was disabled to avoid a filesystem hardlink-cache diagnostic, with no source/gate change.
- Existing five1000-event benchmark medians: parse13.197ms, collection44.575ms, full verification28.015ms; parse allocator peak1,158,808B. Local informational observations, not a network or production SLA.
- Ruff/format, strict mypy, exact symbol maps, complete file guide and privacy/pin/link invariants passed.
- Shared CI advisory repaired narrowly: filelock4.1.1→4.2.1 with [official PyPI hashes](https://pypi.org/pypi/filelock/4.2.1/json) and [maintainer patched-version confirmation](https://github.com/tox-dev/filelock/security/advisories/GHSA-2g95-wg33-c5x2). Pip check and full locked advisory audit passed with no known vulnerabilities; no ignores or gate reductions.

Hosted OS/security/CodeQL/native advisory lanes await publication. Bookmarks are private assertions; no custody/original rows change. A supplied matching checkpoint is not proof of independent storage; handoffs remain pseudonymized, not anonymized. No real evidence, live collection, remote upload or system settings were accessed.
