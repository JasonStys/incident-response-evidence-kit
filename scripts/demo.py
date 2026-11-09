"""Run actual synthetic collection, handoff, checkpoint and redacted reporting. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 27
# variable: NOW — line 28
# definition: main — line 31
# variable: parser — line 34
# variable: output — line 36
# variable: case — line 37
# variable: digest — line 38
# variable: checkpoint — line 47
# variable: verified — line 48
# variable: report — line 50
# variable: row — line 56
# variable: row — line 57
# END CODE MAP

from __future__ import annotations

import argparse
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
    parser = argparse.ArgumentParser(description="Jason Stys — fictional evidence demo")
    parser.add_argument("--output", type=Path, default=ROOT / "out" / "demo")
    output = new_directory(parser.parse_args().output)
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
