# Formats, privacy and integrity contracts

Created by Jason Stys.

## Accepted input

Explicit `jsonl`, `csv`, or `opaque` is mandatory; file extensions are not trusted. JSONL accepts exactly one complete object per physical line, no blanks/duplicate keys/NaN/deep JSON. CSV requires the exact ordered header `event_id,timestamp,kind,actor,asset,message`; quoted commas and multiline messages are preserved. Unknown/missing/extra fields, duplicate event IDs within a source, inconsistent CSV width, NUL, invalid UTF8/escaped surrogates and limits reject the **whole import**, not selected rows. Source line means JSONL line number or CSV record's ending physical line. Repeated event IDs across different sources are retained rather than falsely deduplicated; only byte-identical same-format file retries dedupe globally. A different format on the same bytes is a conflict.

`opaque` preserves any bounded regular-file bytes without interpreting, extracting or executing them; it is not a claim to understand every file format. Empty opaque files are valid. No compressed/archive parser, packet capture parser, PDF OCR or automatic folder discovery exists. Case file counts also bound many empty files.

## Event schema

All six input fields are nonempty strings. `message`<=4096characters, others<=256. `kind` is exactly one of `auth_failure`, `auth_success`, `process_start`, `connection`, `blocked`, `configuration`, `alert`. Event IDs/actor/asset/messages stay private. Timestamps require `YYYY-MM-DDTHH:MM:SS[.ffffff]Z` or a known numeric±HH:MM offset no greater than±14hours. Unknown `-00:00`, naive/local/DST-ambiguous values, leap seconds, >6fractiondigits and normalized years outside2000–2100 reject. No loss of precision by truncation. Store both original string and fixed-width microsecond UTC. Explicit offsets distinguish repeated fall-back hours; clocks themselves are unverified. Timeline ties use evidence digest/source line, not arbitrary import order.

## Acquisition/provenance

Caller authorizes a specific path. Before/open/after descriptor metadata checks catch ordinary source changes. Existing symlink/junction components are rejected; POSIX uses O_NOFOLLOW/O_NONBLOCK. Parent directories, OS administrators and local processes with equivalent privileges are trusted; this is not race-free hostile-directory traversal protection on all OSes. Hashes cover bytes actually copied, not proof of their historical origin. Metadata checks are not a write blocker or a substitute for a read-only forensic image.

Collection-source and operator codes are bounded lowercase slugs, never automatically collected usernames/pathnames. A separate controlled collection procedure must map codes to actual authority/location/person/clock/handling circumstances; this app does not authenticate that mapping. Each canonical custody payload commits its sequence/predecessor plus source code, byte count, format, event count and normalized commitment. Genesis commits key hash/case ID/schema. Verification checks the complete sequence and ties every evidence row to exactly one collection entry. SQL triggers reject updates/deletes, but host admins can bypass them.

## Checkpoints

Exact object `{schema:1,case_id:<32hex>,seq:<positive integer>,head:<64hex>}`. Boolean-as-integer is rejected. A pin for another case, missing/truncated prefix or differing hash rejects. An older genuine prefix can coexist with later extensions. `anchored=true` means **a supplied checkpoint matched**; the software cannot know whether you actually protected that file independently. Store/check a copy outside the case's trust boundary. It cannot authenticate original source truth, attacker-written data before the first pin or changes exclusively after an old pin.

## Public review projection

JSON fields are fixed: schema, author, case_ref, anchored, total_events, filter_matches, more_available and timeline. Rows expose only UTC, allowlisted kind, actor/asset/evidence HMAC pseudonyms and source line. Original event IDs/raw hashes/paths/operator codes/source labels/messages/key never enter the projection. Names/emails/IPs in private message or identity fields are not copied to report. HMAC pseudonyms are domain-separated and case-specific, with96-bit displayed suffixes; pseudonyms are not authorization tokens and negligible collision risk is not zero. Same-case correlation is intentional. UTC/patterns/counts/lines may still reidentify people, so **not anonymization** and no automatic external sharing.

HTML uses escaping, CSPdefault-srcnone and no scripts/remote assets/forms. CSV uses fixed columns and formula-prefix defense-in-depth. Filters use parameterized SQL; end is exclusive, start inclusive. API keyset cursors are private canonical `(UTC,digest,line)` values, not signed client tokens; no network API exposes them. A bounded export labels more_available instead of pretending to include the entire case. Errors expose stable categories/record number without input snippets, passwords or filenames. Raw Python APIs returning private verification state/digests are for trusted local operators, not public responses.
