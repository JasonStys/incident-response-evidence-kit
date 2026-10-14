"""Disposable synthetic evidence fixtures; never read real accounts or host logs. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: NOW — line 21
# definition: event — line 24
# parameter: changes — line 24
# parameter: event_id — line 24
# parameter: timestamp — line 24
# definition: case — line 38
# parameter: tmp_path — line 38
# definition: sample — line 44
# parameter: tmp_path — line 44
# variable: path — line 46
# END CODE MAP

import json

import pytest

from irkit.store import Case

NOW = "2026-10-10T16:03:00Z"


def event(event_id="demo", timestamp="2026-10-10T09:00:00-07:00", **changes):
    """Return exactly six fields with privacy/XSS/formula sentinels for negative export assertions."""
    return {
        "event_id": event_id,
        "timestamp": timestamp,
        "kind": "auth_failure",
        "actor": "private-person@example.invalid",
        "asset": "203.0.113.7",
        "message": "password=PRIVATE-SENTINEL <script>alert('x')</script> =HYPERLINK('evil')",
        **changes,
    }


@pytest.fixture
def case(tmp_path):
    """Create one new case per test, always under pytest-owned local temporary storage."""
    return Case.create(tmp_path / "case", "analyst-a", NOW)


@pytest.fixture
def sample(tmp_path):
    """Write only a synthetic JSONL event; callers receive its explicit authorized path."""
    path = tmp_path / "input.jsonl"
    path.write_text(json.dumps(event()) + "\n", encoding="utf-8")
    return path
