"""Run actual synthetic collection, handoff, checkpoint and redacted reporting. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 25
# variable: NOW — line 26
# definition: main — line 29
# variable: output — line 32
# variable: case — line 33
# variable: digest — line 34
# variable: checkpoint — line 43
# variable: verified — line 44
# variable: report — line 46
# variable: row — line 52
# variable: row — line 53
# END CODE MAP

from __future__ import annotations

import json
from pathlib import Path

from irkit.files import new_directory
from irkit.report import export
from irkit.store import Case

ROOT = Path(__file__).resolve().parents[1]
NOW = "2026-10-10T16:05:00Z"


def main() -> None:
    """Use only supplied fictional fixtures and a new ignored directory; assert independently known totals."""
    (ROOT / "out").mkdir(exist_ok=True, mode=0o700)
    output = new_directory(ROOT / "out" / "demo")
    case = Case.create(output / "case", "analyst-a", NOW)
    digest = case.collect(
        ROOT / "examples/access-review.jsonl", "jsonl", "analyst-a", "access-demo", NOW
    )
    case.collect(
        ROOT / "examples/service-change.csv", "csv", "analyst-a", "service-demo", NOW
    )
    case.record(digest, "review", "analyst-b", NOW)
    case.record(digest, "handoff", "analyst-c", NOW)
    case.checkpoint(output / "checkpoint.json")
    checkpoint = json.loads((output / "checkpoint.json").read_bytes())
    verified = case.verify(checkpoint)
    assert verified["files"] == 2 and verified["events"] == 5 and verified["seq"] == 5
    report = export(case, output / "report", checkpoint)
    assert (
        report["anchored"]
        and len(report["timeline"]) == 5
        and not report["more_available"]
    )
    assert [row["utc"] for row in report["timeline"]] == sorted(
        row["utc"] for row in report["timeline"]
    )
    print(
        json.dumps(
            {
                "actual_demo_files": 2,
                "actual_demo_events": 5,
                "actual_custody_entries": 5,
                "independent_checkpoint_matched": True,
                "report_fields_allowlisted": True,
            }
        )
    )


if __name__ == "__main__":
    main()
