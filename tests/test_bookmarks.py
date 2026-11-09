"""Independent exact-line sidecar, privacy, stale-case and operator handoff tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: NOW — line 64
# definition: prepared — line 67
# parameter: tmp_path — line 67
# variable: case — line 69
# variable: digest — line 70
# variable: checkpoint — line 73
# variable: pin — line 75
# variable: selections — line 76
# definition: test_exact_lines_and_minimized_handoff — line 89
# parameter: tmp_path — line 89
# variable: case — line 91
# variable: digest — line 91
# variable: pin — line 91
# variable: selections — line 91
# variable: original — line 92
# variable: report — line 93
# variable: row — line 95
# variable: output — line 101
# variable: combined — line 103
# variable: path — line 103
# variable: path — line 110
# definition: test_ambiguous_annotations_refused — line 137
# parameter: bad — line 137
# parameter: tmp_path — line 137
# variable: case — line 139
# variable: digest — line 139
# variable: pin — line 139
# variable: selections — line 139
# variable: row — line 140
# definition: test_checkpoint_and_tamper_fail_closed — line 169
# parameter: tmp_path — line 169
# variable: _ — line 171
# variable: case — line 171
# variable: pin — line 171
# variable: selections — line 171
# variable: bad — line 176
# variable: connection — line 179
# definition: test_actual_analyst_cli — line 185
# parameter: capsys — line 185
# parameter: tmp_path — line 185
# variable: _ — line 187
# variable: case — line 187
# variable: pin — line 187
# variable: selections — line 187
# variable: checkpoint — line 188
# variable: sidecar — line 190
# variable: output — line 205
# variable: args — line 206
# END CODE MAP

import copy
import json
from pathlib import Path

import pytest

from irkit.__main__ import main
from irkit.bookmarks import export, review, template
from irkit.contracts import EvidenceError, canonical, json_value
from irkit.store import Case

NOW = "2026-10-10T16:00:00Z"


def prepared(tmp_path: Path) -> tuple[Case, object, dict[str, object], str]:
    """Acquire actual fictional source bytes and bind an annotation to a known original record."""
    case = Case.create(tmp_path / "case", "analyst-a", NOW)
    digest = case.collect(
        Path("examples/access-review.jsonl"), "jsonl", "analyst-a", "access-demo", NOW
    )
    checkpoint = tmp_path / "checkpoint.json"
    case.checkpoint(checkpoint)
    pin = json_value(checkpoint.read_bytes())
    selections = template(case, pin)
    selections["entries"] = [
        {
            "evidence_sha256": digest,
            "line": 1,
            "tag": "needs-context",
            "operator": "analyst-b",
            "note": "PRIVATE-NOTE-SENTINEL <script>must not export</script>",
        }
    ]
    return case, pin, selections, digest


def test_exact_lines_and_minimized_handoff(tmp_path: Path) -> None:
    """Private notes and raw provenance stay outside a verified, pseudonymized selected-event copy."""
    case, pin, selections, digest = prepared(tmp_path)
    original = case.database.read_bytes()
    report = review(case, selections, pin)
    assert len(report["timeline"]) == 1
    row = report["timeline"][0]
    assert row["line"] == 1 and row["tag"] == "needs-context"
    assert row["evidence"].startswith("evidence-") and row["annotation_ref"].startswith(
        "annotation-"
    )
    assert report["checkpoint_matched"]
    output = tmp_path / "handoff"
    export(report, output)
    combined = b"".join(path.read_bytes() for path in output.iterdir()).decode()
    assert digest not in combined and selections["case_id"] not in combined
    assert (
        "PRIVATE-NOTE-SENTINEL" not in combined
        and "analyst-b" not in combined
        and "<script>" not in combined
    )
    assert set(path.name for path in output.iterdir()) == {
        "handoff.json",
        "handoff.html",
    }
    assert case.database.read_bytes() == original
    with pytest.raises(OSError):
        export(report, output)
    assert report == review(case, selections, pin)


@pytest.mark.parametrize(
    "bad",
    [
        "schema",
        "fields",
        "bound",
        "duplicate",
        "digest",
        "line",
        "missing-line",
        "tag",
        "operator",
        "note",
        "control",
        "stale",
    ],
)
def test_ambiguous_annotations_refused(tmp_path: Path, bad: str) -> None:
    """A note can reference only one current original record, never silently attach to a different event."""
    case, pin, selections, digest = prepared(tmp_path)
    row = selections["entries"][0]
    if bad == "schema":
        selections["schema"] = True
    elif bad == "fields":
        row["extra"] = "ignored?"
    elif bad == "bound":
        selections["entries"] = []
    elif bad == "duplicate":
        selections["entries"].append(copy.deepcopy(row))
    elif bad == "digest":
        row["evidence_sha256"] = "0" * 64
    elif bad == "line":
        row["line"] = True
    elif bad == "missing-line":
        row["line"] = 400
    elif bad == "tag":
        row["tag"] = "confirmed-attacker"
    elif bad == "operator":
        row["operator"] = "real full name"
    elif bad == "note":
        row["note"] = "   "
    elif bad == "control":
        row["note"] = "private\nmessage"
    else:
        case.record(digest, "review", "analyst-c", NOW)
    with pytest.raises(EvidenceError):
        review(case, selections, pin)


def test_checkpoint_and_tamper_fail_closed(tmp_path: Path) -> None:
    """No anchor, mismatched anchor or corrupted bytes can produce a checked handoff."""
    case, pin, selections, _ = prepared(tmp_path)
    with pytest.raises(EvidenceError):
        template(case, None)
    with pytest.raises(EvidenceError):
        review(case, selections, None)
    bad = {**pin, "head": "0" * 64}
    with pytest.raises(EvidenceError):
        review(case, selections, bad)
    with case.connection(write=True) as connection:
        connection.execute("DROP TRIGGER evidence_no_update")
    with pytest.raises(EvidenceError):
        review(case, selections, pin)


def test_actual_analyst_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Run template/edit/bookmarks commands exactly as the analyst workflow describes."""
    case, pin, selections, _ = prepared(tmp_path)
    checkpoint = tmp_path / "pin.json"
    checkpoint.write_bytes(canonical(pin))
    sidecar = tmp_path / "template.json"
    assert (
        main(
            [
                "bookmark-template",
                str(case.root),
                str(sidecar),
                "--checkpoint",
                str(checkpoint),
            ]
        )
        == 0
    )
    assert json.loads(sidecar.read_bytes())["entries"] == []
    sidecar.write_bytes(canonical(selections))
    output = tmp_path / "handoff"
    args = [
        "bookmarks",
        str(case.root),
        str(output),
        "--checkpoint",
        str(checkpoint),
        "--selections",
        str(sidecar),
    ]
    assert main(args) == 0
    assert "Minimized selected handoff: 1 rows" in capsys.readouterr().out
    assert main(args) == 2
    assert "rejected" in capsys.readouterr().out
    assert (
        json.loads((output / "handoff.json").read_bytes())["timeline"][0]["line"] == 1
    )
