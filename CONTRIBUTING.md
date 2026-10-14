# Contribution and maintenance

Created by Jason Stys. Keep the source shallow, typed and self-documenting. Use maintained libraries for crypto; do not add an ad-hoc hash/cipher or remote collector. Choose languages for actual boundaries. Describe function inputs/outputs/state/invariants/failure modes; update exact generated file headers and READMEfile purposes after formatting.

Run [all validation commands](docs/testing.md), preserve warnings-as-errors and at least 95% statement+branch coverage for all authored runtime code. Add an independent oracle and meaningful negative regression for every schema/storage/privacy change. New adapters must reject malformed complete batches, preserve original bytes/source time and remain bounded; new event kinds require explicit review because they enter reports.

Regenerate maps `python scripts/code_map.py`; stage intended files then `python scripts/file_guide.py`. Recheck both. Run Rust formatting before maps, since source comments refer to exact lines. Tests/benchmarks/examples must be synthetic/authorized open data with clear provenance. Do not publish ignored `out/`, cases, tokens, keys/certificates or private paths. Audits have no ignores. Pin Actions by full commit SHA and dependencies/compilers exactly; document a version review rather than silent drift.

Publication checklist includes source-bound completed Actions, report review, clean tree and storage check. Never infer permission for account cleanup; ask Jason and verify private backups first. No paid services, production deployment, Windows security settings or local Docker repair is part of contribution. Authored code is MIT; third-party licenses are retained. Open a concise issue for nonsensitive help with a synthetic fixture/version, never a real investigation.
