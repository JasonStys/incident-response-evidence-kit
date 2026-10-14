"""Local-only evidence CLI with explicit authorization and safe error output. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: main — line 31
# parameter: argv — line 31
# variable: parser — line 33
# variable: commands — line 36
# variable: name — line 37
# variable: command — line 38
# variable: args — line 80
# variable: now — line 82
# variable: case — line 85
# variable: checkpoint — line 90
# variable: digest — line 96
# variable: verified — line 107
# variable: report — line 113
# END CODE MAP

from __future__ import annotations

import argparse
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from .contracts import EvidenceError, json_value
from .files import read_file
from .report import export
from .store import Case


def main(argv: list[str] | None = None) -> int:
    """Dispatch init/collect/record/checkpoint/verify/export; never echo source payloads or secrets."""
    parser = argparse.ArgumentParser(
        description="Incident Response Evidence Kit — created by Jason Stys. Local private evidence; no network or extraction."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "collect", "record", "checkpoint", "verify", "export"):
        command = commands.add_parser(name)
        command.add_argument("case", type=Path)
        if name in {"init", "collect", "record"}:
            command.add_argument(
                "--operator",
                required=True,
                help="A nonidentifying operator code, e.g. analyst-a",
            )
        if name == "collect":
            command.add_argument("file", type=Path)
            command.add_argument(
                "--format", choices=["jsonl", "csv", "opaque"], required=True
            )
            command.add_argument(
                "--source",
                required=True,
                help="Approved collection-source reference, not a person name",
            )
            command.add_argument(
                "--ack-authorized",
                action="store_true",
                required=True,
                help="You are authorized to collect this specific file",
            )
        if name == "record":
            command.add_argument("digest")
            command.add_argument(
                "--action", choices=["review", "handoff"], required=True
            )
        if name in {"checkpoint", "export"}:
            command.add_argument("output", type=Path)
        if name in {"verify", "export"}:
            command.add_argument(
                "--checkpoint",
                type=Path,
                help="Independently protected prefix checkpoint; never infer authenticity from the same disk",
            )
        if name == "export":
            command.add_argument("--kind")
            command.add_argument("--start")
            command.add_argument("--end")
            command.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args(argv)
    try:
        now = (
            datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
        )
        case = (
            Case.create(args.case, args.operator, now)
            if args.command == "init"
            else Case(args.case)
        )
        checkpoint = (
            json_value(read_file(args.checkpoint, 1024))
            if getattr(args, "checkpoint", None)
            else None
        )
        if args.command == "collect":
            digest = case.collect(
                args.file, args.format, args.operator, args.source, now
            )
            print(
                f"Private evidence reference: {digest}; keep this reference in authorized records"
            )
        elif args.command == "record":
            case.record(args.digest, args.action, args.operator, now)
        elif args.command == "checkpoint":
            case.checkpoint(args.output)
        elif args.command == "verify":
            verified = case.verify(checkpoint)
            print(
                f"Verified {verified['files']} files / {verified['events']} events; anchored={verified['anchored']}"
            )
            return 0
        elif args.command == "export":
            report = export(
                case,
                args.output,
                checkpoint,
                kind=args.kind,
                start=args.start,
                end=args.end,
                limit=args.limit,
            )
            print(
                f"Exported {len(report['timeline'])} pseudonymized rows; review before sharing"
            )
            return 0
        print("Operation completed; private provenance remains in the case database")
        return 0
    except EvidenceError as error:
        print(f"Operation rejected: {error}")
        return 2
    except (OSError, sqlite3.Error):
        print(
            "Operation rejected: local_storage_error; inspect authorized storage privately"
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
