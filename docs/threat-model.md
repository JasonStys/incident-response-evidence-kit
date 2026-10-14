# Threat model and deliberate limits

Created by Jason Stys. Scope is one authorized operator's trusted local environment.

| Risk / boundary | Protection and actual verification | Residual limitation |
| --- | --- | --- |
| Malformed/untrusted logs | Exact runtime schemas, byte/record/field bounds, atomic rejection, duplicate/NUL/surrogate/NaN/time tests | No malware sandbox; opaque bytes can still be dangerous if opened in another program |
| Altered raw/normalized evidence | SHA256, original BLOB reparse, row comparisons and custody commitments; adversarial SQLite edits tested | Hash equality does not prove source authenticity or truthful timestamps |
| Unauthorized history rewrite | Mutation-blocking triggers and separately saved prefix pins; **internally consistent** rewrite/truncate tests | Admin with all copies/key/pins can rewrite them; pin independence is an operator responsibility |
| Secret/person information in report | Approved-field projection, private message exclusion, HMAC pseudonyms, sentinel tests | Times/patterns/counts can identify people; reviewing recipient/scope remains mandatory |
| XSS/CSV injection | HTML escaping+CSP+no scripts/remotes; fixed CSV columns and formula guards | No guarantee about an arbitrary spreadsheet/browser extension or deliberately modified export |
| Path traversal/device/symlink/races | Explicit file, regular descriptor, no-follow where available, metadata consistency, exclusive new output | Trusted parent/OS boundary; no guarantee against privileged parent swaps, malicious filesystem or same-user interference |
| Corrupt/malicious case database | Size/row/byte checks, quick_check/FK, schema commitment, safe error normalization | SQLite native engine and host installation trusted; not a hardened parser sandbox for adversarial databases |
| Concurrent / interrupted writes | BEGINIMMEDIATE, rollback/finally close, dedupe constraints; actual multithread and injected exception tests | No process-kill, power-loss, filesystem durability or busy-volume stress qualification |
| Supply chain / CI token theft | Full Action SHAs, exact Cargo.lock/dev hashes, advisory/secret/CodeQL gates, no checkout persisted credentials | Installers/runners/advisory feeds are trusted dependencies, not provenance certification |
| Private local files | New POSIX0700directory/0600files, ignored private paths, no runtime network | Plaintext SQLite; Windows mode bits do not impose full ACLs; use trusted OS ACLs and encrypted disk |

No encryption-at-rest implementation, multi-user authentication, external upload, automatic legal verdict, remote agent, incident containment, adversary scanning or production hosting exists. No FIPS validation, government/military certification or legal-admissibility assertion. Local administrators can read database key and original evidence, memory and temp data. Python cannot guarantee string/key zeroization. Secure deletion/retention must follow your organization's approved tools; the application never destroys evidence. Review the [runbook](runbook.md) before any authorized non-demo use.
