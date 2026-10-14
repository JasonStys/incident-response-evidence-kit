"""Measure bounded synthetic parsing/SQLite collection/reverification; no speedup or SLA claim. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 34
# definition: main — line 37
# variable: output — line 40
# variable: data — line 41
# variable: number — line 52
# variable: elapsed — line 55
# variable: _ — line 58
# variable: peak — line 58
# variable: number — line 60
# variable: case — line 61
# variable: started — line 64
# variable: started — line 67
# variable: started — line 76
# variable: report — line 79
# variable: name — line 88
# variable: values — line 88
# END CODE MAP

from __future__ import annotations

import json
import platform
import statistics
import time
import tracemalloc
from pathlib import Path

from irkit.files import new_directory, write_new
from irkit.parsing import parse
from irkit.store import Case

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Measure five actual 1000-event batches; peak is Python allocator bytes, not process RSS."""
    (ROOT / "out").mkdir(exist_ok=True, mode=0o700)
    output = new_directory(ROOT / "out/benchmark")
    data = "\n".join(
        json.dumps(
            {
                "event_id": f"synthetic-{number}",
                "timestamp": "2026-10-10T16:00:00Z",
                "kind": "alert",
                "actor": "fictional@example.invalid",
                "asset": "192.0.2.10",
                "message": "Synthetic performance fixture",
            }
        )
        for number in range(1000)
    ).encode()
    write_new(output / "input.jsonl", data)
    elapsed = {"parse_ms": [], "collect_ms": [], "verify_ms": []}
    tracemalloc.start()
    assert len(parse(data, "jsonl")) == 1000
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    for number in range(5):
        case = Case.create(
            output / f"case-{number}", "analyst-a", "2026-10-10T16:00:00Z"
        )
        started = time.perf_counter()
        assert len(parse(data, "jsonl")) == 1000
        elapsed["parse_ms"].append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        case.collect(
            output / "input.jsonl",
            "jsonl",
            "analyst-a",
            "host-demo",
            "2026-10-10T16:00:00Z",
        )
        elapsed["collect_ms"].append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        assert case.verify()["events"] == 1000
        elapsed["verify_ms"].append((time.perf_counter() - started) * 1000)
    report = {
        "schema": 1,
        "python": platform.python_version(),
        "os": platform.system(),
        "events_per_batch": 1000,
        "input_bytes": len(data),
        "repeats": 5,
        "parse_python_peak_bytes": peak,
        "median_ms": {
            name: statistics.median(values) for name, values in elapsed.items()
        },
        "samples_ms": elapsed,
        "scope": "Actual local synthetic timings; collection includes file I/O, SQLite insert/commit and genesis verification; verification reparses bytes/rechecks database, not network collection. Parse allocation peak is not RSS. Informational, not an SLA or comparative speedup.",
    }
    write_new(output / "report.json", json.dumps(report, indent=2).encode() + b"\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
