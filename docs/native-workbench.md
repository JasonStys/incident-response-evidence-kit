# Native evidence-case workbench

Created by Jason Stys. Version 1.1.0 adds a Windows portable application, not an installer or a separate demonstration program. Publication and PC installation require separate acceptance; this source recipe performs neither.

## Create, collect and inspect

Open `IncidentResponseEvidenceKit.exe`. No separately installed Python, Node, account, default password or first-launch network connection is required. Inputs, Findings and Saved analyses tabs provide the actual workflows, alongside Help, bundled Licenses and Exit application. The version-independent OS-local `JasonStys/IncidentResponseEvidenceKit` application-data directory stays outside the installation. The explicit Existing case field still supports original CLI case directories.

1. Select **Create a new private case**, a new managed name, nonidentifying operator reference and custody clock with an explicit offset. Acknowledge permission and Run. Up to eight managed case directories are admitted; existing cases are never reset.
2. Select **Collect authorized source file**. Choose JSONL, CSV or opaque input, its actual format and a nonidentifying source reference. The original engine atomically stores exact bytes, normalized events, commitments and custody. Byte-identical retries deduplicate; malformed structured input never silently becomes opaque.
3. **Inspect private timeline** using kind, inclusive start, exclusive end and page size 1–1000. Rows expose private identities, original SHA256 and source line. Literal search filters this saved page, not the whole case. The pagination detail view retains full matching count and more-available status.
4. **Prepare next timeline page** restores the saved page's original input context and a case/head/filter-bound cursor. Review and Run explicitly. Changed custody or filters invalidate the cursor. Each verified page is a separate history bundle.
5. **Verify case integrity** or **Record custody assertion** against an exact collected digest. Operator labels, source clocks and asserted custody are not independently authenticated people, timing or physical possession.

Prepared access-review steps only populate these ordinary controls; they never run automatically or collect this PC's logs.

## Checkpoints and selected handoffs

**Save private checkpoint** puts a small private pin in its output bundle. Export that bundle into a new private directory, then select `private-checkpoint.json` as the checkpoint input. A checkpoint kept in this same profile/export is not proof of independent storage. Retain a copy in separately trusted storage for an external prefix anchor.

**Export minimized timeline** uses the original allowlisted pseudonymized JSON/HTML/CSV projection, with true counts and truncation. Original messages, actor identities, source hashes and case identifiers are omitted. Timing and activity patterns may still identify people: pseudonymized does not mean anonymous.

For a single event, reopen an original private timeline page, select its row and click **Prepare selected event bookmark**. Exact source digest/line populate ordinary controls. Supply the checkpoint and private note/tag/operator, then Run. The original resolver re-verifies the case and resolves that record. Its `handoff.json`/`handoff.html` omit private notes, operator labels and original identities/hashes. **Prepare private bookmark template** and the optional closed-schema sidecar support the existing multi-selection workflow. Checkpoint inputs are bounded to 4 KiB and bookmark sidecars to 4 MiB. A custody change makes an old sidecar stale; deliberately rereview it.

The general **Export selected analysis bundle** copies every file in that selected bundle, including PRIVATE timeline/checkpoint/template data when present. It does not sanitize an arbitrary bundle. Only explicitly minimized operations produce the minimized schemas; review the file purposes before sharing.

## Local storage and failures

Original BLOBs and the case pseudonym key remain in the original private case database. GUI history stores metadata, selected pages and actual output bundles, never duplicate original BLOBs. Both stores are plaintext OS-owner data, not a multiuser encrypted service. Back up the full closed profile and external cases separately. No collector, arbitrary command/plugin, listener, upload, remote AI or automatic deletion is involved.

Original limits remain 20 MiB/file, 64 MiB raw case evidence, 256 files, 50,000 events and 10,000 custody entries. Imported-case admission requires ordinary application tables, bounded metadata/custody fetches, a SQLite value limit of 20 MiB plus 64 KiB and a 20-million-instruction connection budget. Hostile views/virtual tables, oversized cells and expensive queries fail closed. These safeguards are not legal/forensic certification or an authenticated trust root.

History permits 20 runs/128 MiB retained bundle payload, 64 MiB/bundle and 32 MiB/file; metadata adds overhead. Full history refuses before another case mutation. Export and explicitly remove a selected saved analysis to manage retention. Removing history never deletes a case, original source or previous export. Original case transactions and later GUI history are separate: a history/disk failure may happen after a valid case commit. **Verify before retrying** a reported failure. Exit drains the owned worker and releases the lock normally; it never force-kills processes.

## Build and independent native acceptance

Use patched Windows CPython 3.14.10 in an isolated environment. Install `requirements-dev.lock` and `requirements-native.lock` with `--require-hashes`; run `python scripts/build_native.py` and `python scripts/test_native_app.py`. Actual Tcl/Tk supplies its own notices, including Tcl9 DLL-embedded resources. Package metadata binds source SHA, dirty status, exact public resources and actual interpreter DLL. Dirty candidates are development evidence; CI requires clean source.

The consumer uses actual widgets, handlers and mainloop in two fresh processes with an explicitly marked synthetic profile. It verifies original bytes, UTC/page oracles, context-bound navigation, selected bookmark minimization, exact exports, invalid-input retention and identical restart bundles. It uploads no package/profile/screenshots. Original Rust/CLI/property/SQLite tests, coverage, advisory scans, secrets, pins and CodeQL remain mandatory. Windows proof does not establish Mac/Linux packaging or Authenticode signing.
