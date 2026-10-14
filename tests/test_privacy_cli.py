"""Actual CLI, public projection, output safety and source-path contracts. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_public_export — line 100
# parameter: case — line 100
# parameter: sample — line 100
# parameter: tmp_path — line 100
# variable: digest — line 102
# variable: checkpoint — line 104
# variable: report — line 105
# variable: path — line 111
# variable: source — line 112
# variable: forbidden — line 113
# variable: html — line 124
# definition: test_export_empty_filter — line 135
# parameter: case — line 135
# parameter: sample — line 135
# parameter: tmp_path — line 135
# variable: report — line 138
# definition: test_formula_guard — line 150
# parameter: value — line 150
# definition: test_plain_cell_and_domains — line 155
# definition: test_html_escape — line 162
# variable: report — line 164
# variable: key — line 168
# variable: html — line 176
# definition: test_cli_all_commands — line 180
# parameter: capsys — line 180
# parameter: sample — line 180
# parameter: tmp_path — line 180
# variable: root — line 182
# variable: connection — line 203
# variable: digest — line 204
# definition: test_cli_rejections — line 240
# parameter: capsys — line 240
# parameter: tmp_path — line 240
# variable: output — line 244
# definition: test_regular_size_exclusive_and_modes — line 262
# parameter: tmp_path — line 262
# variable: path — line 264
# variable: directory — line 274
# definition: test_link_rejection — line 280
# parameter: monkeypatch — line 280
# parameter: tmp_path — line 280
# variable: path — line 282
# parameter: self — line 283
# definition: test_native_symlink_rejection — line 288
# parameter: tmp_path — line 288
# variable: target — line 291
# variable: link — line 293
# definition: test_acquisition_race_boundaries — line 301
# parameter: boundary — line 301
# parameter: monkeypatch — line 301
# parameter: tmp_path — line 301
# variable: path — line 303
# variable: original — line 305
# variable: values — line 306
# variable: name — line 308
# variable: calls — line 317
# definition: changed_stat — line 319
# parameter: descriptor — line 319
# variable: calls — line 322
# variable: changed — line 323
# definition: test_read_growth_after_stat — line 337
# parameter: monkeypatch — line 337
# parameter: tmp_path — line 337
# variable: path — line 339
# variable: original — line 341
# definition: short_stat — line 343
# parameter: args — line 343
# parameter: kwargs — line 343
# parameter: self — line 343
# variable: result — line 345
# variable: values — line 347
# variable: name — line 349
# definition: test_cli_os_error — line 365
# parameter: capsys — line 365
# parameter: tmp_path — line 365
# definition: test_module_entrypoint — line 374
# parameter: monkeypatch — line 374
# parameter: tmp_path — line 374
# variable: context — line 382
# variable: error — line 384
# END CODE MAP

import json
import os
import runpy
import sys
from types import SimpleNamespace

import pytest
from conftest import NOW

from irkit.__main__ import main
from irkit.contracts import EvidenceError
from irkit.files import checked_path, new_directory, read_file, write_new
from irkit.report import export, html_report, reference, spreadsheet_cell


def test_public_export(case, sample, tmp_path):
    """All three output types omit raw identities/messages/paths/digests and preserve approved timeline order."""
    digest = case.collect(sample, "jsonl", "analyst-a", "host-demo", NOW)
    case.checkpoint(tmp_path / "pin.json")
    checkpoint = json.loads((tmp_path / "pin.json").read_text())
    report = export(case, tmp_path / "report", checkpoint)
    assert (
        report["anchored"]
        and report["total_events"] == 1
        and not report["more_available"]
    )
    for path in (tmp_path / "report").iterdir():
        source = path.read_text()
        for forbidden in (
            "PRIVATE-SENTINEL",
            "private-person",
            "203.0.113.7",
            "<script>",
            "password=",
            digest,
            str(sample),
            "analyst-a",
        ):
            assert forbidden not in source
    html = (tmp_path / "report" / "report.html").read_text()
    assert (
        "default-src 'none'" in html
        and "not anonymized" in html
        and "Jason Stys" in html
    )
    assert len(report["timeline"][0]["actor"]) == len("actor-") + 24
    with pytest.raises(FileExistsError):
        export(case, tmp_path / "report")


def test_export_empty_filter(case, sample, tmp_path):
    """An empty filtered timeline is represented explicitly, without losing the full-case count."""
    case.collect(sample, "jsonl", "analyst-a", "host-demo", NOW)
    report = export(case, tmp_path / "report", kind="alert")
    assert (
        report["timeline"] == []
        and report["filter_matches"] == 0
        and report["total_events"] == 1
    )


@pytest.mark.parametrize(
    "value",
    ["=CMD()", "+CMD()", "-CMD()", "@CMD()", "  =CMD()", "\ttext", "\rtext", "\ntext"],
)
def test_formula_guard(value):
    """Potential spreadsheet formulas/control prefixes are forced to plain text."""
    assert spreadsheet_cell(value) == "'" + value


def test_plain_cell_and_domains():
    """Safe cells remain intact; HMAC identities differ by case key and semantic domain."""
    assert spreadsheet_cell("plain") == "plain"
    assert reference(b"a" * 32, "actor", "x") != reference(b"a" * 32, "asset", "x")
    assert reference(b"a" * 32, "actor", "x") != reference(b"b" * 32, "actor", "x")


def test_html_escape():
    """Renderer escapes even deliberately corrupted display fields, retaining an inert page."""
    report = {
        "timeline": [
            {
                key: '<img src=x onerror="bad">'
                for key in ("utc", "kind", "actor", "asset", "evidence", "line")
            }
        ],
        "anchored": False,
        "total_events": 1,
        "filter_matches": 1,
        "more_available": False,
    }
    html = html_report(report)
    assert "<img" not in html and "&lt;img" in html


def test_cli_all_commands(tmp_path, sample, capsys):
    """Exercise every real CLI command using actual SQLite, private checkpoint and reports."""
    root = tmp_path / "cli-case"
    assert main(["init", str(root), "--operator", "analyst-a"]) == 0
    assert (
        main(
            [
                "collect",
                str(root),
                str(sample),
                "--format",
                "jsonl",
                "--source",
                "host-demo",
                "--operator",
                "analyst-a",
                "--ack-authorized",
            ]
        )
        == 0
    )
    from irkit.store import Case

    with Case(root).connection() as connection:
        digest = connection.execute("SELECT digest FROM evidence").fetchone()[0]
    assert (
        main(
            [
                "record",
                str(root),
                digest,
                "--action",
                "review",
                "--operator",
                "analyst-b",
            ]
        )
        == 0
    )
    assert main(["checkpoint", str(root), str(tmp_path / "pin.json")]) == 0
    assert main(["verify", str(root), "--checkpoint", str(tmp_path / "pin.json")]) == 0
    assert (
        main(
            [
                "export",
                str(root),
                str(tmp_path / "report"),
                "--checkpoint",
                str(tmp_path / "pin.json"),
                "--kind",
                "auth_failure",
                "--limit",
                "1",
            ]
        )
        == 0
    )
    assert "PRIVATE" not in capsys.readouterr().out


def test_cli_rejections(tmp_path, capsys):
    """Application errors and filesystem errors expose only generic categories, not private path contents."""
    assert main(["init", str(tmp_path / "case"), "--operator", "../bad"]) == 2
    assert main(["verify", str(tmp_path / "missing")]) == 2
    output = capsys.readouterr().out
    assert str(tmp_path) not in output and "Operation rejected" in output
    with pytest.raises(SystemExit):
        main(
            [
                "collect",
                str(tmp_path),
                "source",
                "--format",
                "opaque",
                "--source",
                "host-demo",
                "--operator",
                "analyst-a",
            ]
        )


def test_regular_size_exclusive_and_modes(tmp_path):
    """Actual file reads are bounded; existing files and directories never get overwritten."""
    path = tmp_path / "input"
    write_new(path, b"abc")
    assert read_file(path, 3) == b"abc"
    with pytest.raises(EvidenceError):
        read_file(path, 2)
    with pytest.raises(EvidenceError):
        read_file(tmp_path)
    with pytest.raises(FileExistsError):
        write_new(path, b"not-overwritten")
    assert read_file(path) == b"abc"
    directory = new_directory(tmp_path / "private")
    if os.name == "posix":
        assert directory.stat().st_mode & 0o777 == 0o700
        assert path.stat().st_mode & 0o777 == 0o600


def test_link_rejection(tmp_path, monkeypatch):
    """Cross-platform guard rejects linked components without requiring Windows symlink privileges."""
    path = tmp_path / "linked"
    monkeypatch.setattr(type(path), "is_symlink", lambda self: self == path)
    with pytest.raises(EvidenceError, match="linked_path_rejected"):
        checked_path(path)


def test_native_symlink_rejection(tmp_path):
    """On POSIX, exercise a real filesystem symlink; Windows uses the no-privilege guard test above."""
    if os.name == "posix":
        target = tmp_path / "original"
        target.write_bytes(b"unchanged")
        link = tmp_path / "link"
        link.symlink_to(target)
        with pytest.raises(EvidenceError):
            read_file(link)
        assert target.read_bytes() == b"unchanged"


@pytest.mark.parametrize("boundary", ["identity", "growth", "metadata"])
def test_acquisition_race_boundaries(tmp_path, monkeypatch, boundary):
    """Inject descriptor identity/growth/metadata changes to prove the source-stability guards reject them."""
    path = tmp_path / "source"
    path.write_bytes(b"abc")
    original = path.stat()
    values = {
        name: getattr(original, name)
        for name in (
            "st_mode",
            "st_dev",
            "st_ino",
            "st_size",
            "st_mtime_ns",
            "st_ctime_ns",
        )
    }
    calls = 0

    def changed_stat(descriptor):
        """Return deliberately inconsistent descriptor metadata at the selected acquisition stage."""
        nonlocal calls
        calls += 1
        changed = dict(values)
        if boundary == "identity":
            changed["st_ino"] += 1
        elif boundary == "metadata" and calls == 2:
            changed["st_mtime_ns"] += 1
        elif boundary == "growth":
            changed["st_size"] = 1
        return SimpleNamespace(**changed)

    monkeypatch.setattr("irkit.files.os.fstat", changed_stat)
    with pytest.raises(EvidenceError):
        read_file(path, 2 if boundary == "growth" else 3)


def test_read_growth_after_stat(tmp_path, monkeypatch):
    """A file growing beyond cap between pathname-stat and descriptor-read fails instead of truncating silently."""
    path = tmp_path / "source"
    path.write_bytes(b"abc")
    original = type(path).stat

    def short_stat(self, *args, **kwargs):
        """Model initial metadata reporting one byte less, preserving regular-file descriptor identity."""
        result = original(self, *args, **kwargs)
        if self == path:
            values = {
                name: getattr(result, name)
                for name in (
                    "st_mode",
                    "st_dev",
                    "st_ino",
                    "st_mtime_ns",
                    "st_ctime_ns",
                )
            }
            return SimpleNamespace(st_size=2, **values)
        return result

    monkeypatch.setattr(type(path), "stat", short_stat)
    with pytest.raises(EvidenceError, match="file_type_or_size"):
        read_file(path, 2)


def test_cli_os_error(tmp_path, capsys):
    """An inaccessible parent becomes a generic storage error with no path disclosure."""
    assert (
        main(["init", str(tmp_path / "missing" / "case"), "--operator", "analyst-a"])
        == 2
    )
    assert "local_storage_error" in capsys.readouterr().out


def test_module_entrypoint(tmp_path, monkeypatch):
    """Exercise actual python-module dispatch, not just the imported main function."""
    monkeypatch.setattr(
        sys,
        "argv",
        ["irkit", "init", str(tmp_path / "module-case"), "--operator", "analyst-a"],
    )
    # Avoid runpy's warning about the earlier imported module without altering the test process binding.
    with monkeypatch.context() as context:
        context.delitem(sys.modules, "irkit.__main__")
        with pytest.raises(SystemExit) as error:
            runpy.run_module("irkit", run_name="__main__")
        assert error.value.code == 0
