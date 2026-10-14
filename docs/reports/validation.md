# Measured validation and release review

Created by Jason Stys. Initial implementation verification is in progress; no pending GitHub result is represented as passed. This report will be updated with completed source-bound CI evidence before final handoff.

Local WindowsPython3.14.6 execution initially passed150tests and99.66%combined statement/branch coverage of all `irkit/` code. The actual two-source demo imported2files/5events/5custody entries and matched its retained checkpoint. Rust1.98.0 compiled4unit tests and compared21actual binary inputs with Pythonhashlib plus an oversize rejection. Later Unicode and independently consistent-rewrite regressions require a fresh acceptance run; earlier counts are not the final release totals.

The selected1000-event benchmark has5actual repeats, no comparative speedup/SLA claim. Scope includes actual parsing, file/SQLitecollection and fullreverification; Python allocation is not totalRSS. Only synthetic aggregate timings/report projections may be checked in. No privatecase, checkpoint/key/rawlog/database or original evidence reference is an uploaded artifact.

## Development findings corrected

- The initial stock Windows virtual-environment ensurepip could not use its host temp directory under the sandbox. Workspace-local process-scoped temporary storage allowed the same standard installer to complete; no host security/ACL setting changed.
- RustCrypto0.11output array lacks the older LowerHex formatting trait. Standard per-byte hex formatting plus independentempty/abcvectors and cross-language tests corrected the compatibility issue, without replacing cryptography.
- An intentionally sabotaging **test fixture** used `with sqlite3.connect()` as though it closed the connection. Python3.14ResourceWarning correctly failed the suite. Explicit closing+commit fixed the fixture; application connections already close in finally. Warnings remain errors.
- Review added escaped Unicode-surrogate rejection before SQLiteencoding, safe HTML scalar escaping, and internally consistent admin rewrite/truncation regressions proving why independently protected checkpoints matter.
- The Rust audit tool version was corrected to registry-verified0.22.2 before publication; no nonexistent/unreviewed tool version is claimed as executed.

## Release checklist

Before final handoff: complete source-bound Actions, zero open CodeQLalerts or documented unresolved findings, full local assertions, current maps/file guide, private data excluded, exactdependencylocks/scannerpins, no artifact/cache writes, clean Git tree and measured public reports. This is source publication, not deployment of a public investigation service.
