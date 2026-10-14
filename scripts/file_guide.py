"""Maintain a complete tracked-file README purpose inventory; unknown file types fail closed. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 32
# variable: BEGIN — line 33
# variable: END — line 33
# variable: SPECIAL — line 34
# definition: purpose — line 56
# parameter: path — line 56
# variable: source — line 60
# variable: line — line 68
# definition: main — line 74
# variable: parser — line 76
# variable: args — line 78
# variable: files — line 79
# variable: rows — line 87
# variable: path — line 88
# variable: label — line 89
# variable: readme — line 91
# variable: original — line 92
# variable: end — line 93
# variable: start — line 93
# variable: expected — line 94
# END CODE MAP

from __future__ import annotations

import argparse
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN, END = "<!-- BEGIN FILE GUIDE -->", "<!-- END FILE GUIDE -->"
SPECIAL = {
    ".gitignore": "Keep original evidence, private databases, checkpoints, tools and working data untracked.",
    ".gitattributes": "Consistent LF source checkout across operating systems.",
    "LICENSE": "MIT terms for authored source; upstream tools retain their licenses.",
    "pyproject.toml": "Strict lint/type/test/statement-and-branch coverage configuration.",
    "tools.lock.json": "Exact official scanner release hashes and compiler version.",
    "requirements-dev.in": "Exact portable development tool inputs.",
    "requirements-dev.lock": "Complete hash-locked portable development graph.",
    "native/Cargo.toml": "Independent Rust bounded streaming SHA256 CLI and exact RustCrypto input.",
    "native/Cargo.lock": "Complete checksum-locked Rust dependency graph; no private input.",
    "native/src/main.rs": "Native safe stdin hashing, known-vector/boundary/I/O/chunk tests and no input echo.",
    "examples/access-review.jsonl": "Fictional access events with mixed offsets and unsorted records, no real accounts.",
    "examples/service-change.csv": "Fictional quoted service-change and alert CSV records, no real organizations.",
    "docs/reports/benchmark.json": "Actual five-batch parsing, SQLite collection/reverification and Python-allocation measurements.",
    "docs/reports/demo.json": "Approved-field projection of five actual fictional SQLite events, no raw messages/identifiers.",
    "docs/reports/demo.html": "Inert escaped rendering of the selected fictional review timeline.",
    "docs/reports/demo.csv": "Fixed-column pseudonymized CSV of the selected fictional review timeline.",
    "docs/reports/local.json": "Source-bound actual local test/coverage counts and native/CLI evidence summary.",
    "docs/reports/ci.json": "Immutable executable-source acceptance snapshot with actual completed Actions checks.",
}


def purpose(path: str) -> str:
    """Require a human-readable purpose for every tracked file, not a generic guessed fallback."""
    if path in SPECIAL:
        return SPECIAL[path]
    source = (ROOT / path).read_text(encoding="utf-8")
    if path.endswith(".py"):
        return (ast.get_docstring(ast.parse(source)) or "").splitlines()[0]
    if path.endswith(".md"):
        return source.splitlines()[0].lstrip("# ") + "."
    if path.endswith((".yml", ".sh", ".hcl", ".sql")) or path == "Dockerfile":
        return next(
            line.lstrip("#- ")
            for line in source.splitlines()
            if line.startswith(("# ", "-- "))
        )
    raise ValueError("tracked-file purpose missing")


def main() -> int:
    """Generate/check exact tracked-file summaries; stage intended files before regeneration."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .rstrip("\0")
        .split("\0")
    )
    if files == [""]:
        raise ValueError("stage intended files first")
    rows = ["| File | Purpose |", "| --- | --- |"]
    for path in sorted(files):
        label = path.replace("_", "\\_")
        rows.append(f"| [{label}]({path}) | {purpose(path).replace('|', '/')} |")
    readme = ROOT / "README.md"
    original = readme.read_text(encoding="utf-8")
    start, end = original.index(BEGIN) + len(BEGIN), original.index(END)
    expected = original[:start] + "\n\n" + "\n".join(rows) + "\n\n" + original[end:]
    if args.check and original != expected:
        raise ValueError("README file guide stale")
    if not args.check:
        readme.write_text(expected, encoding="utf-8", newline="\n")
    print(f"README inventory current: {len(files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
