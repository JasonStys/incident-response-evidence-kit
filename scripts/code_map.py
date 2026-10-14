"""Generate/check exact Python, SQL, shell and YAML symbol positions. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: BEGIN — line 108
# variable: END — line 109
# variable: ROOT — line 110
# definition: mapped — line 113
# parameter: source — line 113
# variable: start — line 116
# variable: finish — line 117
# variable: source — line 118
# variable: tree — line 119
# variable: first — line 120
# variable: insertion — line 121
# variable: records — line 128
# variable: node — line 129
# variable: count — line 138
# variable: header — line 139
# variable: kind — line 143
# variable: line — line 143
# variable: name — line 143
# parameter: item — line 144
# variable: lines — line 149
# definition: main — line 154
# variable: parser — line 156
# variable: arguments — line 158
# variable: stale — line 159
# variable: folder — line 160
# variable: path — line 161
# variable: original — line 162
# variable: expected — line 163
# variable: tree — line 165
# variable: node — line 166
# variable: path — line 177
# variable: original — line 191
# variable: expected — line 192
# variable: path — line 197
# variable: original — line 198
# variable: expected — line 199
# definition: shell_mapped — line 208
# parameter: source — line 208
# parameter: suffix — line 208
# variable: prefix — line 210
# variable: begin — line 211
# variable: end — line 211
# variable: start — line 213
# variable: finish — line 214
# variable: source — line 215
# variable: lines — line 216
# variable: insertion — line 217
# variable: insertion — line 219
# variable: records — line 220
# variable: line — line 221
# variable: number — line 221
# variable: name — line 224
# variable: name — line 226
# variable: name — line 229
# variable: name — line 232
# variable: name — line 237
# variable: name — line 240
# variable: name — line 242
# variable: name — line 244
# variable: name — line 246
# variable: name — line 250
# variable: part — line 255
# variable: name — line 257
# variable: name — line 262
# variable: name — line 264
# variable: name — line 266
# variable: name — line 268
# variable: count — line 272
# variable: header — line 273
# variable: kind — line 277
# variable: name — line 277
# variable: number — line 277
# definition: rust_mapped — line 285
# parameter: source — line 285
# variable: begin — line 287
# variable: end — line 287
# variable: start — line 289
# variable: finish — line 290
# variable: source — line 291
# variable: lines — line 292
# variable: insertion — line 293
# variable: insertion — line 295
# variable: records — line 296
# variable: line — line 297
# variable: number — line 297
# variable: kind — line 300
# variable: name — line 300
# variable: names — line 304
# variable: name — line 305
# variable: name — line 308
# variable: name — line 313
# variable: count — line 315
# variable: header — line 316
# variable: kind — line 320
# variable: name — line 320
# variable: number — line 320
# END CODE MAP

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

BEGIN = "# BEGIN CODE MAP (generated; python scripts/code_map.py)"
END = "# END CODE MAP"
ROOT = Path(__file__).resolve().parents[1]


def mapped(source: str) -> str:
    """Build a self-consistent line map for definitions, parameters and assigned variables."""
    if "\n" + BEGIN + "\n" in source:
        start = source.index("\n" + BEGIN + "\n") + 1
        finish = source.index("\n" + END + "\n", start) + len(END) + 2
        source = source[:start] + source[finish:]
    tree = ast.parse(source)
    first = tree.body[0] if tree.body else None
    insertion = (
        first.end_lineno
        if isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
        else 0
    )
    records: set[tuple[str, str, int]] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            records.add(("definition", node.name, node.lineno))
        elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
            records.add(("attribute", node.attr, node.lineno))
        elif isinstance(node, ast.arg):
            records.add(("parameter", node.arg, node.lineno))
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            records.add(("variable", node.id, node.lineno))
    count = len(records) + 2
    header = (
        [BEGIN]
        + [
            f"# {kind}: {name} — line {line + count if line > insertion else line}"
            for kind, name, line in sorted(
                records, key=lambda item: (item[2], item[0], item[1])
            )
        ]
        + [END]
    )
    lines = source.splitlines(keepends=True)
    lines.insert(insertion or 0, "\n".join(header) + "\n")
    return "".join(lines)


def main() -> int:
    """Update authored Python files, or fail if --check finds stale maps or missing contracts."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    stale = []
    for folder in ("irkit", "scripts", "tests"):
        for path in sorted((ROOT / folder).glob("*.py")):
            original = path.read_text(encoding="utf-8")
            expected = mapped(original)
            if arguments.check:
                tree = ast.parse(original)
                for node in ast.walk(tree):
                    if isinstance(
                        node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                    ) and not ast.get_docstring(node):
                        raise ValueError(
                            f"Missing function/class contract: {path.name}:{node.lineno}"
                        )
            if original != expected:
                stale.append(str(path.relative_to(ROOT)))
                if not arguments.check:
                    path.write_text(expected, encoding="utf-8", newline="\n")
    for path in [
        *(ROOT / "scripts").glob("*.ps1"),
        *(ROOT / "scripts").glob("*.sh"),
        *(ROOT / "ops").rglob("*.yml"),
        *(ROOT / "ops").glob("*.hcl"),
        *(ROOT / "ops").glob("*.sh"),
        *(ROOT / "gitops").rglob("*.yml"),
        *(ROOT / "chart").rglob("*.yaml"),
        *(ROOT / "sql").rglob("*.sql"),
        *(ROOT / ".github/workflows").glob("*.yml"),
        *(ROOT / "infra").rglob("*.tf"),
        *(ROOT / "infra").rglob("*.tftest.hcl"),
        *(ROOT / "policies").glob("*.rego"),
    ]:
        original = path.read_text(encoding="utf-8")
        expected = shell_mapped(original, path.suffix)
        if original != expected:
            stale.append(str(path.relative_to(ROOT)))
            if not arguments.check:
                path.write_text(expected, encoding="utf-8", newline="\n")
    for path in (ROOT / "native/src").glob("*.rs"):
        original = path.read_text(encoding="utf-8")
        expected = rust_mapped(original)
        if original != expected:
            stale.append(str(path.relative_to(ROOT)))
            if not arguments.check:
                path.write_text(expected, encoding="utf-8", newline="\n")
    print("Code maps current" if not stale else "Code maps: " + ", ".join(stale))
    return 1 if arguments.check and stale else 0


def shell_mapped(source: str, suffix: str) -> str:
    """Map shell symbols, SQL columns/tables and YAML parameters/controls/expressions without execution."""
    prefix = "--" if suffix == ".sql" else "#"
    begin, end = BEGIN.replace("#", prefix, 1), END.replace("#", prefix, 1)
    if "\n" + begin + "\n" in source:
        start = source.index("\n" + begin + "\n") + 1
        finish = source.index("\n" + end + "\n", start) + len(end) + 2
        source = source[:start] + source[finish:]
    lines = source.splitlines(keepends=True)
    insertion = 1 if source.startswith("#!") else 0
    while insertion < len(lines) and lines[insertion].startswith(prefix):
        insertion += 1
    records = {}
    for number, line in enumerate(lines, 1):
        if line.lstrip().startswith(prefix):
            continue
        for name in re.findall(r"\$([A-Za-z_][A-Za-z_0-9]*)", line):
            records.setdefault(("variable", name), number)
        for name in re.findall(r"^function ([A-Za-z0-9_-]+)", line):
            records[("function", name)] = number
        if suffix == ".sh":
            for name in re.findall(r"^(?:export )?([A-Za-z_][A-Za-z_0-9]*)=", line):
                records.setdefault(("variable", name), number)
        if suffix == ".sql":
            for name in re.findall(
                r"\b([A-Za-z_][A-Za-z_0-9]*) (?:TEXT|INTEGER|BLOB|BIGINT|TIMESTAMPTZ)\b",
                line,
            ):
                records.setdefault(("column", name), number)
            for name in re.findall(r"CREATE TABLE (\w+)", line):
                records[("table", name)] = number
        elif suffix in {".tf", ".hcl", ".rego"}:
            for name in re.findall(r"^\s*(\w+)(?:\([^)]*\))?\s+if\b", line):
                records.setdefault(("rule", name), number)
            for name in re.findall(r"\b(?:every|some)\s+(\w+)\b", line):
                records.setdefault(("variable", name), number)
            for name in re.findall(r"^\s*default\s+(\w+)\s*:=", line):
                records.setdefault(("default", name), number)
            for name in re.findall(
                r"^\s*([A-Za-z_][A-Za-z0-9_.]*)\s*(?:=|:=|if\b)", line
            ):
                records.setdefault(("symbol", name), number)
            for name in re.findall(
                r'^\s*(?:variable|resource|run|mock_resource) "([^"]+)"(?: "([^"]+)")?',
                line,
            ):
                records.setdefault(
                    ("block", ".".join(part for part in name if part)), number
                )
            for name in re.findall(
                r"\b(?:var|local|count|input)\.[A-Za-z0-9_.]+", line
            ):
                records.setdefault(("reference", name), number)
        elif suffix in {".yml", ".yaml"}:
            for name in re.findall(r"^\s*(?:- )?([A-Za-z_][A-Za-z_0-9]*):", line):
                records.setdefault(("parameter", name), number)
            for name in re.findall(r"^\s*- id: ([A-Za-z0-9_-]+)", line):
                records[("control", name)] = number
            for name in re.findall(r"\$\{\{\s*([A-Za-z0-9_.]+)\s*\}\}", line):
                records.setdefault(("expression", name), number)
            for name in re.findall(r"\.(?:Values|Release)\.[A-Za-z_0-9]+", line):
                records.setdefault(("template-reference", name), number)
            if "| quote" in line:
                records.setdefault(("template-function", "quote"), number)
    count = len(records) + 2
    header = [
        begin,
        *(
            f"{prefix} {kind}: {name} — line {number + count if number > insertion else number}"
            for (kind, name), number in records.items()
        ),
        end,
    ]
    lines.insert(insertion, "\n".join(header) + "\n")
    return "".join(lines)


def rust_mapped(source: str) -> str:
    """Map reviewed Rust function/constant/let declarations and parameters after rustfmt, without execution."""
    begin, end = "// BEGIN CODE MAP", "// END CODE MAP"
    if begin in source:
        start = source.index(begin)
        finish = source.index(end, start) + len(end) + 1
        source = source[:start] + source[finish:]
    lines = source.splitlines(keepends=True)
    insertion = 0
    while insertion < len(lines) and lines[insertion].startswith("//!"):
        insertion += 1
    records = []
    for number, line in enumerate(lines, 1):
        if line.lstrip().startswith("//"):
            continue
        for kind, name in re.findall(
            r"\b(fn|const|struct|let)\s+(?:mut\s+)?([a-zA-Z_][a-zA-Z_0-9]*)", line
        ):
            records.append((kind, name, number))
        for names in re.findall(r"(?:let|Ok)\s*\(?\(([^)]+)\)", line):
            for name in names.split(","):
                if name.strip().isidentifier():
                    records.append(("binding", name.strip(), number))
        for name in re.findall(
            r"(?:[(,]|\bmut)\s*([a-zA-Z_][a-zA-Z_0-9]*):\s*(?:&|impl|u\d|\[)", line
        ):
            records.append(("parameter", name, number))
        if "for " in line:
            for name in re.findall(r"\bfor ([a-zA-Z_][a-zA-Z_0-9]*) in", line):
                records.append(("variable", name, number))
    count = len(records) + 2
    header = [
        begin,
        *(
            f"// {kind}: {name} — line {number + count if number > insertion else number}"
            for kind, name, number in records
        ),
        end,
    ]
    lines.insert(insertion, "\n".join(header) + "\n")
    return "".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
