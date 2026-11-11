"""Real frozen widget/core/history/export and honest failure-evidence acceptance. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: capture — line 115
# parameter: target — line 115
# parameter: window — line 115
# variable: load — line 121
# variable: gdi — line 122
# variable: user — line 122
# variable: pointer — line 123
# variable: arguments — line 124
# variable: library — line 124
# variable: name — line 124
# variable: result — line 124
# variable: function — line 150
# attribute: argtypes — line 151
# attribute: restype — line 151
# variable: handle — line 154
# variable: rectangle — line 155
# variable: height — line 158
# variable: width — line 158
# variable: source — line 161
# variable: destination — line 162
# variable: bitmap — line 163
# variable: previous — line 164
# variable: pixels — line 169
# variable: header — line 170
# variable: raw — line 188
# variable: scanlines — line 189
# variable: row — line 190
# variable: column — line 192
# variable: offset — line 193
# definition: chunk — line 196
# parameter: data — line 196
# parameter: name — line 196
# definition: oracle — line 218
# parameter: files — line 218
# parameter: index — line 218
# variable: value — line 221
# variable: row — line 226
# variable: row — line 227
# variable: row — line 232
# variable: value — line 239
# variable: raw — line 243
# variable: value — line 248
# variable: raw — line 251
# variable: value — line 255
# definition: exercise — line 265
# parameter: output — line 265
# parameter: reopen — line 265
# parameter: window — line 265
# variable: deadline — line 270
# variable: expected — line 271
# variable: receipt — line 272
# variable: pin_path — line 289
# definition: finish — line 291
# parameter: failed — line 291
# attribute: acceptance_result — line 293
# variable: name — line 298
# variable: raw — line 298
# variable: row — line 300
# definition: checked — line 307
# parameter: callback — line 307
# definition: wait — line 315
# parameter: callback — line 315
# definition: layout — line 325
# variable: widgets — line 330
# variable: name — line 331
# variable: widget — line 333
# definition: rejected — line 353
# definition: completed — line 360
# parameter: index — line 360
# variable: files — line 367
# variable: case — line 373
# variable: connection — line 374
# variable: parent — line 394
# variable: target — line 400
# variable: path — line 401
# variable: pin_path — line 402
# variable: parent — line 407
# variable: target — line 413
# variable: path — line 414
# variable: bad — line 415
# definition: start — line 424
# parameter: index — line 424
# variable: scenario_index — line 437
# variable: external — line 441
# variable: row — line 455
# definition: begin — line 468
# variable: identity — line 474
# variable: verified — line 479
# END CODE MAP

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import struct
import sys
import time
import zlib
from pathlib import Path
from typing import TYPE_CHECKING, Any

from irkit import desktop_project as project
from irkit.desktop_io import json_value

if TYPE_CHECKING:
    from tkinter import ttk

    from irkit.desktop import Workbench


def capture(window: Workbench, target: Path) -> None:
    """Capture only this owned synthetic Tk window via PrintWindow, never the user's whole desktop."""
    if sys.platform != "win32":
        raise OSError("native screenshot acceptance targets Windows")
    from ctypes import wintypes

    load = ctypes.WinDLL
    user, gdi = load("user32", use_last_error=True), load("gdi32", use_last_error=True)
    pointer = ctypes.c_void_p
    for library, name, arguments, result in [
        (user, "GetAncestor", [pointer, ctypes.c_uint], pointer),
        (user, "GetWindowDC", [pointer], pointer),
        (gdi, "CreateCompatibleDC", [pointer], pointer),
        (gdi, "CreateCompatibleBitmap", [pointer, ctypes.c_int, ctypes.c_int], pointer),
        (gdi, "SelectObject", [pointer, pointer], pointer),
        (gdi, "DeleteObject", [pointer], ctypes.c_int),
        (gdi, "DeleteDC", [pointer], ctypes.c_int),
        (user, "ReleaseDC", [pointer, pointer], ctypes.c_int),
        (user, "PrintWindow", [pointer, pointer, ctypes.c_uint], ctypes.c_int),
        (user, "GetWindowRect", [pointer, ctypes.POINTER(wintypes.RECT)], ctypes.c_int),
        (
            gdi,
            "GetDIBits",
            [
                pointer,
                pointer,
                ctypes.c_uint,
                ctypes.c_uint,
                pointer,
                pointer,
                ctypes.c_uint,
            ],
            ctypes.c_int,
        ),
    ]:
        function = getattr(library, name)
        function.argtypes, function.restype = arguments, result
    # Flush this owned native window's pending control messages before reading its pixels.
    window.root.update()
    handle = user.GetAncestor(window.root.winfo_id(), 2)
    rectangle = wintypes.RECT()
    if not user.GetWindowRect(handle, ctypes.byref(rectangle)):
        raise OSError("owned window bounds unavailable")
    width, height = rectangle.right - rectangle.left, rectangle.bottom - rectangle.top
    if not 1 <= width <= 4096 or not 1 <= height <= 4096:
        raise OSError("owned screenshot outside bounded dimensions")
    source = user.GetWindowDC(handle)
    destination = gdi.CreateCompatibleDC(source)
    bitmap = gdi.CreateCompatibleBitmap(source, width, height)
    previous = gdi.SelectObject(destination, bitmap)
    try:
        if not user.PrintWindow(handle, destination, 2):
            raise OSError("owned window rendering unavailable")
        gdi.SelectObject(destination, previous)
        pixels = ctypes.create_string_buffer(width * height * 4)
        header = ctypes.create_string_buffer(
            struct.pack(
                "<IiiHHIIiiII",
                40,
                width,
                -height,
                1,
                32,
                0,
                width * height * 4,
                0,
                0,
                0,
                0,
            )
        )
        if gdi.GetDIBits(source, bitmap, 0, height, pixels, header, 0) != height:
            raise OSError("owned screenshot pixels incomplete")
        raw = pixels.raw
        scanlines = bytearray()
        for row in range(height):
            scanlines.append(0)
            for column in range(width):
                offset = (row * width + column) * 4
                scanlines.extend((raw[offset + 2], raw[offset + 1], raw[offset]))

        def chunk(name: bytes, data: bytes) -> bytes:
            """Encode a bounded standard PNG chunk with its actual CRC."""
            return (
                struct.pack(">I", len(data))
                + name
                + data
                + struct.pack(">I", zlib.crc32(name + data))
            )

        target.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(scanlines)))
            + chunk(b"IEND", b"")
        )
    finally:
        gdi.SelectObject(destination, previous)
        gdi.DeleteObject(bitmap)
        gdi.DeleteDC(destination)
        user.ReleaseDC(handle, source)


def oracle(index: int, files: dict[str, bytes]) -> None:
    """Literal original-case outcomes distinguish real acquisition, pages and minimization from a normal EXE exit."""
    if index in (3, 4, 5):
        value = json_value(files["result.json"])
        assert value["filter_matches"] == 5
        assert len(value["records"]) == (1 if index == 5 else 2)
        assert value["more_available"] is (index != 5)
        if index == 3:
            assert [row["line"] for row in value["records"]] == [2, 3]
            assert [row["utc"] for row in value["records"]] == [
                "2026-10-10T16:00:00.000000Z",
                "2026-10-10T16:00:30.000000Z",
            ]
        if index == 4:
            assert [row["kind"] for row in value["records"]] == [
                "configuration",
                "blocked",
            ]
        if index == 5:
            assert value["records"][0]["kind"] == "alert"
    elif index == 8:
        value = json_value(files["report.json"])
        assert value["total_events"] == 5 and len(value["timeline"]) == 5
        assert set(files) == {"report.json", "report.html", "timeline.csv"}
        assert all(
            b"fictional-analyst@example.invalid" not in raw for raw in files.values()
        )
    elif index == 9:
        assert json_value(files["private-bookmarks.json"])["entries"] == []
    elif index == 10:
        value = json_value(files["handoff.json"])
        assert len(value["timeline"]) == 1 and value["timeline"][0]["line"] == 2
        assert value["timeline"][0]["tag"] == "needs-context"
        for raw in files.values():
            assert b"PRIVATE-SYNTHETIC-REVIEW-NOTE" not in raw
            assert b"fictional-analyst@example.invalid" not in raw
    else:
        value = json_value(files["result.json"])["verification"]
        assert value["files"] == (0 if index == 0 else 1 if index == 1 else 2)
        assert value["events"] == (0 if index == 0 else 3 if index == 1 else 5)
        assert value["seq"] == (
            1 if index == 0 else 2 if index == 1 else 4 if index in (11, 12) else 3
        )
        if index == 12:
            assert value["anchored"] is True


def exercise(window: Workbench, output: Path, reopen: bool) -> None:
    """Drive the identical real Tk widgets, core transactions and normal shutdown in a fresh synthetic profile only."""
    from unittest.mock import patch

    output.mkdir(mode=0o700)
    deadline = time.monotonic() + 55
    expected = 13
    receipt: dict[str, Any] = {
        "schema": 1,
        "product": project.PRODUCT,
        "version": project.VERSION,
        "source": window.identity.get("source"),
        "source_dirty": window.identity.get("source_dirty"),
        "python_version": sys.version.split()[0],
        "python_dll_sha256": window.identity.get("python_dll_sha256"),
        "pid": os.getpid(),
        "parent_pid": os.getppid(),
        "synthetic": True,
        "reopen": reopen,
        "passed": False,
        "steps": [],
        "tcl_version": str(window.root.tk.call("info", "patchlevel")),
        "tk_version": str(window.root.tk.call("package", "require", "Tk")),
    }
    pin_path: Path | None = None

    def finish(failed: bool = False) -> None:
        """Retain bounded aggregate evidence and exact bundle hashes; request ordinary application shutdown."""
        window.acceptance_result = not failed
        receipt["passed"] = not failed
        receipt["bundles"] = {
            str(row["id"]): {
                name: hashlib.sha256(raw).hexdigest()
                for name, raw in window.state.files(row["id"]).items()
            }
            for row in window.state.history()
        }
        (output / "acceptance.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf8"
        )
        window.exit()

    def checked(callback: Any) -> None:
        """An actual oracle failure is retained, never retried or substituted by precomputed outputs."""
        try:
            callback()
        except Exception:
            receipt["failure_stage"] = callback.__name__
            finish(True)

    def wait(callback: Any) -> None:
        """Poll only this owned live worker under one fixed deadline while normal Tk callbacks run."""
        if time.monotonic() > deadline:
            receipt["failure_stage"] = "owned-operation-deadline"
            finish(True)
        elif window.busy:
            window.root.after(60, lambda: wait(callback))
        else:
            checked(callback)

    def layout() -> None:
        """Prove current active inputs, Run and lifecycle controls fit the supported actual minimum size."""
        window.root.geometry("980x700")
        window.tabs.tk.call(str(window.tabs), "select", str(window.inputs_page))
        window.root.update()
        widgets: list[ttk.Widget] = [window.run_button, *window.footer_buttons.values()]
        for name in project.ACTIVE_FIELDS[window.mode.get()]:
            widgets.extend(window.field_widgets[name])
        for widget in widgets:
            assert widget.winfo_ismapped()
            assert widget.winfo_rootx() >= window.root.winfo_rootx()
            assert widget.winfo_rooty() >= window.root.winfo_rooty()
            assert (
                widget.winfo_rootx() + widget.winfo_width()
                <= window.root.winfo_rootx() + window.root.winfo_width()
            )
            assert (
                widget.winfo_rooty() + widget.winfo_height()
                <= window.root.winfo_rooty() + window.root.winfo_height()
            )
        receipt["minimum_layout"] = {
            "width": 980,
            "height": 700,
            "activeInputsRunAndLifecycleVisible": True,
        }
        window.root.geometry("1260x860")
        window.root.update()

    def rejected() -> None:
        """Invalid context must leave all original completed bundles and the case unchanged."""
        assert len(window.state.history()) == expected
        assert "rejected" in window.status.get().lower()
        receipt["steps"].append("actual-invalid-checkpoint-retains-case-and-history")
        finish()

    def completed(index: int) -> None:
        """Check real saved outputs and independent source-byte oracles after each actual widget operation."""
        nonlocal pin_path
        assert (
            len(window.state.history()) == index + 1
            and window.selected_run == index + 1
        )
        files = window.state.files(index + 1)
        oracle(index, files)
        receipt["steps"].append("actual-case-workflow-" + str(index + 1))
        if index == 1:
            from irkit.store import Case

            case = Case(window.state.path / "cases/fictional-access-review")
            with case.connection() as connection:
                assert (
                    connection.execute("SELECT raw FROM evidence").fetchone()[0]
                    == (project.ROOT / "examples/access-review.jsonl").read_bytes()
                )
        if index in (3, 10):
            window.table.selection_set("0")
            window.inspect()
            window.root.update()
            assert json.loads(window.details.get("1.0", "end"))["line"] == 2
            capture(
                window,
                output
                / (
                    "selected-evidence.png"
                    if index == 3
                    else "owner-unknown-review.png"
                ),
            )
        if index == 7:
            parent = output / "private-checkpoint-export"
            parent.mkdir()
            with patch(
                "irkit.desktop.filedialog.askdirectory", return_value=str(parent)
            ):
                window.export_button.invoke()
            target = next(parent.iterdir())
            assert {path.name: path.read_bytes() for path in target.iterdir()} == files
            pin_path = target / "private-checkpoint.json"
            receipt["steps"].append(
                "actual-exported-private-checkpoint-not-independent-storage-claim"
            )
        if index + 1 == expected:
            parent = output / "private-export"
            parent.mkdir()
            with patch(
                "irkit.desktop.filedialog.askdirectory", return_value=str(parent)
            ):
                window.export_button.invoke()
            target = next(parent.iterdir())
            assert {path.name: path.read_bytes() for path in target.iterdir()} == files
            bad = output / "wrong-checkpoint.json"
            bad.write_text('{"schema":1,"case_id":"wrong","seq":1,"head":"bad"}')
            window.values["checkpoint"].set(str(bad))
            window.authorized.set(True)
            window.run_button.invoke()
            wait(rejected)
        else:
            start(index + 1)

    def start(index: int) -> None:
        """Prepare fixtures only through ordinary fields; navigation/bookmark actions use their actual saved-row handlers."""
        if index in (4, 5):
            assert window.review_button is not None
            window.review_button.invoke()
            assert window.values["cursor"].get() and not window.authorized.get()
        elif index == 10:
            window.show(4)
            window.table.selection_set("0")
            window.bookmark_button.invoke()
            window.values["checkpoint"].set(str(pin_path))
            window.values["note"].set("PRIVATE-SYNTHETIC-REVIEW-NOTE")
        else:
            scenario_index = (0, 1, 2, 3, 0, 0, 4, 5, 6, 4, 4, 4, 4)[index]
            window.prepared.set(project.SCENARIOS[scenario_index])
            window.load_prepared()
            if index == 1:
                external = output / "selected-external-events.jsonl"
                external.write_bytes(
                    (project.ROOT / "examples/access-review.jsonl").read_bytes()
                )
                with patch(
                    "irkit.desktop.filedialog.askopenfilename",
                    return_value=str(external),
                ):
                    window.choose("input", "file")
            if index == 9:
                window.mode.set(project.MODES[7])
                window.values["checkpoint"].set(str(pin_path))
            if index == 11:
                window.mode.set(project.MODES[4])
                row = json_value(window.state.files(4)["result.json"])["records"][0]
                window.values["digest"].set(row["evidence_sha256"])
                window.values["action"].set("review")
                window.values["clock"].set("2026-10-10T16:04:00Z")
            if index == 12:
                window.values["checkpoint"].set(str(pin_path))
        window.show_fields()
        layout()
        assert not window.authorized.get()
        window.authorized.set(True)
        window.run_button.invoke()
        wait(lambda: completed(index))

    def begin() -> None:
        """A second process opens all identical saved bundles and the actual original case without recomputing history."""
        if reopen:
            from irkit.store import Case

            assert len(window.state.history()) == expected
            for identity in range(1, expected + 1):
                window.history_table.selection_set(str(identity))
                window.open_button.invoke()
                assert window.selected_run == identity
                oracle(identity - 1, window.state.files(identity))
            verified = Case(
                window.state.path / "cases/fictional-access-review"
            ).verify()
            assert (
                verified["events"] == 5
                and verified["files"] == 2
                and verified["seq"] == 4
            )
            receipt["steps"].append(
                "actual-process-reopen-all-exact-bundles-and-preserved-case"
            )
            finish()
        else:
            window.run_button.invoke()
            assert (
                window.state.history() == []
                and "permission" in window.status.get().lower()
            )
            start(0)

    checked(begin)
