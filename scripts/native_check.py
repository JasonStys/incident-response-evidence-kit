"""Cross-language SHA256 and actual CLI rejection oracle, only against this built binary. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 24
# definition: main — line 27
# variable: binary — line 29
# variable: generator — line 36
# variable: inputs — line 37
# variable: size — line 39
# variable: path — line 63
# variable: data — line 65
# variable: result — line 66
# variable: result — line 74
# END CODE MAP

from __future__ import annotations

import hashlib
import json
import os
import random
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Compare 20 seeded byte buffers/real fixture files and one over-limit CLI failure with Python hashlib."""
    binary = (
        ROOT
        / "native"
        / "target"
        / "release"
        / ("evidence-digest.exe" if os.name == "nt" else "evidence-digest")
    )
    generator = random.Random(42)
    inputs = [
        generator.randbytes(size)
        for size in (
            0,
            1,
            2,
            3,
            63,
            64,
            65,
            127,
            128,
            129,
            255,
            256,
            511,
            512,
            513,
            8191,
            8192,
            8193,
            65536,
            20971520,
        )
    ]
    inputs.extend(
        path.read_bytes() for path in sorted((ROOT / "examples").glob("*.jsonl"))
    )
    for data in inputs:
        result = subprocess.run(
            [str(binary)], input=data, capture_output=True, timeout=30, check=True
        )
        assert result.stdout.decode().split() == [
            str(len(data)),
            hashlib.sha256(data).hexdigest(),
        ]
        assert not result.stderr
    result = subprocess.run(
        [str(binary)],
        input=b"x" * (20971520 + 1),
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert (
        result.returncode == 2
        and not result.stdout
        and result.stderr.strip() == b"evidence_read_or_size_error"
    )
    print(
        json.dumps(
            {
                "native_cross_language_cases": len(inputs),
                "oversize_rejected": True,
                "maximum_bytes": 20971520,
            }
        )
    )


if __name__ == "__main__":
    main()
