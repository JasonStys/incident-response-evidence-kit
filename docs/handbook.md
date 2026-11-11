# Incident Response Evidence Kit handbook

By Jason Stys.

Create exact-digest/line analyst bookmarks and minimized handoffs from one verified SQLite evidence snapshot.

Lets analysts share necessary findings while retaining chain/checkpoint bindings and excluding raw originals and notes.

## Read the documentation

| Edition | Audience and contents |
| --- | --- |
| [project-guide.docx](reports/project-guide.docx) | User and developer guide: purpose, current usage, design, boundaries and source references. |

The editable Markdown remains the maintenance source. The Word files are readable editions, and the workbook is an evidence index rather than a test runner. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [runbook](runbook.md)

### Design and contracts

- [architecture](architecture.md)
- [contracts](contracts.md)
- [research](research.md)
- [threat model](threat-model.md)

### Security and validation

- [testing](testing.md)

## Historical results and reproduction

The reviewed source is [`dbf51a335ec512ad4f1f1485e434c5207eaf62cf`](https://github.com/JasonStys/incident-response-evidence-kit/tree/dbf51a335ec512ad4f1f1485e434c5207eaf62cf). The observed functional workflow baseline is `dbf51a335ec512ad4f1f1485e434c5207eaf62cf`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/bookmarks-2026-11-09.md)
- [Current Actions](https://github.com/JasonStys/incident-response-evidence-kit/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Analyst notes and tags are private assertions, not incident attribution.
- A matching checkpoint does not prove that a copy is independently stored.
- Minimized pseudonymized handoffs are not anonymous; review identifying evidence before sharing.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.

## Current graphical workflows

- [Native usage, file formats and privacy](native-workbench.md).
- [Native workflow validation scope](reports/native-workbench-2026-11-10.md).

Earlier Office editions and benchmark reports retain their dated source scope; they do not establish acceptance of a later native package.
