# Test strategy and reproducible verification

Created by Jason Stys. Real execution, not synthetic pass-status generation.

| Layer | Tests / oracle | Failure boundaries |
| --- | --- | --- |
| Contract / unit | Exact UTC expected values, fixed digest vectors, JSON/CSV/schema guards | Naive/DST/unknown offsets, leap second, fraction truncation, unknown fields, duplicates, UTF8/surrogates, NUL, oversized data |
| Property | Hypothesis microsecond identity and Unicode quoted CSV roundtrip | No replacement/discarding or precision loss |
| Real SQLite integration | Exact original BLOB, atomic malformed-batch rejection, exception rollback, triggers, real FKs | Partial import, unexpected schema/version, tampered bytes/events/custody/key/metadata |
| Authentication boundary | Correctly rehashed/admin-rewritten history **passes unanchored internal consistency but fails an original prefix pin** | False promise that same-disk hashes authenticate custody; prefix truncation |
| Concurrency | Eight actual separate connections for duplicate collect and custody appends | Duplicate evidence/sequence, broken predecessor chain, lost updates |
| Query / contract | Stable timezone ties, keyset pages, exclusive end, kind filter, actual EXPLAINQUERYPLAN index assertion | Missing/duplicated pages, SQL interpolation, invalid range/limits |
| Privacy / output | Secret/name/email/IP/path/hash sentinels omitted from all three files; HTML escaping/formula guards; new-file/directory preservation | Raw messages or identifiers copied to public review; output overwrite |
| CLI / E2E | Every actual subcommand and module entry; two supplied real SQLite sources/five events/five custody entries | Missing authorization acknowledgement, unsafe error/path snippets, fake verification |
| Native | Rust4known-vector/boundary/I/O/chunk tests; 21Python-vs-compiled-binary cases plus actual oversize exit2 | Digest mismatch, >20MiB partial success, input echo/unsafe code |
| Supply chain | Hash-locked Python development graph; exact Cargo graph/advisory audit; full-history secret scan; pinned scanners/Actions; CodeQLPythonsecurityextended | Unreviewed versions/permissions, ignored vulnerability/advisory findings, hidden uploads/caches |

Application coverage denominator is **all `irkit/` authored code, statement+branch**, >=95%; no exclusions/skips. Tooling scripts and SQL/Rust are not in Python coverage. SQL is executed by integration tests; Rust has compiler/Clippy/tests and interop oracles, not a claimed measured native coverage percentage. POSIX real symlink/mode tests run only when POSIX; Windows also tests guards without requiring elevated symlink privilege. No disabled warning filters.

Reproduce Python validation from a fresh checkout:

```text
python -m pip install --require-hashes -r requirements-dev.lock
python -m ruff check irkit scripts tests
python -m ruff format --check irkit scripts tests
python -m mypy
python scripts/code_map.py --check
python scripts/file_guide.py --check
python scripts/validate_repo.py
python -m pytest --cov --junitxml=out/tests.xml --cov-report=json:out/coverage.json
python -m scripts.demo
python -m scripts.benchmark
```

On the GitHub four native OS/Python lanes, `scripts/validate.sh` fails fast. Native Rust lane uses exact1.98.0 compiler, rustfmtcheck, Clippydenywarnings, cargo test/build--locked and native_check; Linux additionally audits Rust dependencies. Security lane audits the Python graph without exclusions, scans complete Git history and validates actual workflow/shell syntax. CodeQL scans Python, **not an assertion that Rust has CodeQL coverage**. No arbitrary private evidence is uploaded in these jobs. Benchmark is informational, not a brittle cross-machine latency gate.

Important untested production gaps: process-kill/power-loss durability, hostile-filesystem racing, many-user load, enforced Windows ACL configurations, encryption restoration, authenticated humans/legal handling, signed external timestamps. No standards conformance/production readiness claim. See measured [validation](reports/validation.md) for executed counts/source/CI IDs rather than this strategy as proof.
