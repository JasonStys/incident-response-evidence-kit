"""Independent strict desktop JSON/file boundaries and native workflow scope checks. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_ambiguous_nonfinite_or_deep_json_is_not_a_checkpoint — line 39
# parameter: payload — line 39
# definition: test_bounded_actual_file_unavailable_and_swapped_descriptor — line 45
# parameter: monkeypatch — line 45
# parameter: tmp_path — line 45
# variable: selected — line 47
# variable: actual — line 56
# definition: changed — line 58
# parameter: descriptor — line 58
# variable: row — line 60
# definition: test_native_ci_requires_real_app_and_retains_original_cross_language_gates — line 68
# variable: root — line 70
# variable: text — line 71
# END CODE MAP

import os
from pathlib import Path

import pytest

from irkit import desktop_io
from irkit.desktop_io import Rejected, json_value, read_bytes


@pytest.mark.parametrize(
    "payload",
    [
        b'{"x":1,"x":2}',
        b'{"x":NaN}',
        b'{"x":1e999}',
        b'{"x":Infinity}',
        b"\xff",
        b"[[[",
        b"[" * 2000,
    ],
)
def test_ambiguous_nonfinite_or_deep_json_is_not_a_checkpoint(payload):
    """A selected pin/sidecar must not acquire last-key-wins or non-finite meanings absent from original contracts."""
    with pytest.raises(Rejected):
        json_value(payload)


def test_bounded_actual_file_unavailable_and_swapped_descriptor(tmp_path, monkeypatch):
    """The reader uses a bounded actual descriptor and rejects a type swap instead of treating a device as a file."""
    selected = tmp_path / "selected.json"
    selected.write_bytes(b"0123456789")
    assert read_bytes(selected, 10) == b"0123456789"
    with pytest.raises(Rejected, match="limit"):
        read_bytes(selected, 9)
    with pytest.raises(Rejected):
        read_bytes(tmp_path / "missing", 10)
    with pytest.raises(Rejected):
        read_bytes(tmp_path, 10)
    actual = desktop_io.os.fstat

    def changed(descriptor):
        """Keep a real descriptor while presenting an independently constructed nonregular metadata observation."""
        row = actual(descriptor)
        return os.stat_result((0, *tuple(row)[1:]))

    monkeypatch.setattr(desktop_io.os, "fstat", changed)
    with pytest.raises(Rejected, match="changed"):
        read_bytes(selected, 10)


def test_native_ci_requires_real_app_and_retains_original_cross_language_gates():
    """A build-only lane or artifact upload is not an acceptable replacement for the original core and actual EXE journeys."""
    root = Path(__file__).resolve().parents[1]
    text = (root / ".github/workflows/ci.yml").read_text(encoding="utf8")
    assert "python-version: '3.14.10'" in text
    assert (
        "python scripts/build_native.py" in text
        and "python scripts/test_native_app.py" in text
    )
    assert "python scripts/native_check.py" in text and "cargo test --locked" in text
    assert "cargo audit --deny warnings" in text and "--require-hashes" in text
    assert "upload-artifact" not in text and "actions/cache" not in text
    assert "pull_request_target" not in text and "continue-on-error" not in text
