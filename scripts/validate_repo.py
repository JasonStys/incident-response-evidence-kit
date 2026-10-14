"""Gate tracked-file privacy, reviewed workflow/crypto bounds and internal documentation links. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 28
# definition: main — line 31
# variable: files — line 33
# variable: name — line 39
# variable: pins — line 47
# variable: tool — line 49
# variable: workflow_text — line 52
# variable: path — line 54
# variable: uses — line 56
# variable: value — line 58
# variable: value — line 62
# variable: native — line 80
# variable: name — line 82
# variable: path — line 85
# variable: target — line 86
# variable: destination — line 89
# END CODE MAP

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Inspect intended Git files only; reject working/private data, stale pins or broken local Markdown links."""
    files = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .strip("\0")
        .split("\0")
    )
    for name in files:
        if (
            name.startswith(("out/", "cases/", ".venv/", ".tools/", "native/target/"))
            or name.endswith((".sqlite", ".db", ".pem", ".key"))
            or ".env" in name
            or "checkpoint" in name.lower()
        ):
            raise ValueError("private or generated data tracked")
    pins = json.loads((ROOT / "tools.lock.json").read_bytes())
    assert pins["rust"] == "1.98.0"
    for tool in pins["tools"].values():
        assert re.fullmatch(r"[0-9a-f]{64}", tool["sha256"])
        assert tool["url"].startswith("https://github.com/")
    workflow_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / ".github/workflows").glob("*.yml")
    )
    uses = re.findall(r"uses:\s*([^\s#]+)", workflow_text)
    assert uses and all(
        re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", value) for value in uses
    )
    assert not any(
        value in workflow_text
        for value in (
            "upload-artifact",
            "actions/cache",
            "cache: true",
            "pull_request_target",
            "write-all",
            "--ignore",
            "continue-on-error",
        )
    )
    assert (
        "persist-credentials: false" in workflow_text
        and "upload-database: false" in workflow_text
    )
    assert (
        "cargo audit --deny warnings" in workflow_text
        and "--require-hashes" in workflow_text
    )
    native = (ROOT / "native/Cargo.toml").read_text()
    assert 'unsafe_code = "forbid"' in native and 'sha2 = "=0.11.1"' in native
    for name in files:
        if not name.endswith(".md"):
            continue
        path = ROOT / name
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            destination = (path.parent / target.split("#")[0]).resolve()
            if not destination.is_relative_to(ROOT) or not destination.exists():
                raise ValueError(f"broken local documentation link in {path.name}")
    print(f"Repository privacy, pins and local links valid: {len(files)} files")


if __name__ == "__main__":
    main()
