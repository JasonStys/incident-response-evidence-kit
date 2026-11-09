# Exact-line bookmarks and minimized handoff

Created by Jason Stys. Analysts can privately annotate selected original evidence lines and create a minimized event handoff without editing evidence, normalized events or the custody chain. An annotation is an analyst assertion, never a new ground-truth incident verdict.

After authorized collection and a separately protected checkpoint:

```text
python -m irkit bookmark-template out/my-case out/private-bookmarks.json --checkpoint out/checkpoint.json
# Edit the private sidecar with exact collected evidence SHA256 and original source line.
python -m irkit bookmarks out/my-case out/selected-handoff --checkpoint out/checkpoint.json --selections out/private-bookmarks.json
```

The blank schema1 template binds `case_id`, current custody `seq` and `head`; keep them unchanged. Add1–1000 `entries`, each with `evidence_sha256`, integer `line`, `tag` (`key-event`, `follow-up`, `needs-context`, `reviewed`), nonidentifying `operator` code and a printable nonblank `note` of at most500 characters. Use the private digest printed at acquisition and the parser's exact original source line, not a row number in a sorted report. Duplicate digest/line pairs are rejected. No incident attribution or automated conclusion is inferred from tags.

The command verifies original BLOBs, normalized rows, schema, custody chain and required checkpoint in one consistent SQLite read transaction, then resolves each selected digest/line by a parameterized exact query. Unknown records, altered evidence, mismatched checkpoints, malformed references or changed current case history reject the handoff. Even a later custody-only review makes the sidecar stale; generate a fresh template and deliberately re-review notes before reuse. A supplied matching prefix checkpoint is not proof it was stored independently; that custody responsibility remains yours.

Only `handoff.json` and escaped scriptless `handoff.html` enter the new output directory. They include selected UTC/kind/tag, case-specific HMAC actor/asset/evidence/annotation references and exact source line. **Private notes, operator codes, messages, originals, raw evidence hashes, case IDs and custody heads are omitted.** Keep the original selections file private; it is never copied into the shareable output. HMAC references bind the source snapshot, checkpoint and selection sidecar without exporting those private values. They do not authenticate a person or encrypt the source database. Review the handoff before sharing: times, patterns, tags and pseudonyms can still identify people. Pseudonymized is not anonymized.

No table, trigger or original byte is modified; old report/acquisition/custody behavior remains unchanged. Output parents must exist and destinations must be new. Runtime inputs remain bounded, including a1MiB selections file and the existing64MiB/50,000-event case bounds. Verification still reparses the whole bounded case; bookmark resolution uses indexed `(evidence_digest,line)` queries and deterministic ordering. No network collection, evidence extraction, remote upload, AI attribution or privilege changes are introduced.
