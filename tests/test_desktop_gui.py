"""Presentation-adapter unit tests with real core/SQLite workers; real widgets are separately frozen-tested. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: Variable — line 236
# definition: __init__ — line 239
# parameter: self — line 239
# parameter: value — line 239
# attribute: callbacks — line 241
# attribute: value — line 241
# definition: get — line 243
# parameter: self — line 243
# definition: set — line 247
# parameter: self — line 247
# parameter: value — line 247
# attribute: value — line 249
# variable: callback — line 250
# definition: trace_add — line 253
# parameter: _event — line 253
# parameter: callback — line 253
# parameter: self — line 253
# definition: Widget — line 258
# definition: __init__ — line 261
# parameter: _args — line 261
# parameter: kwargs — line 261
# parameter: self — line 261
# attribute: options — line 263
# attribute: rows — line 263
# attribute: selected — line 263
# attribute: flags — line 264
# attribute: tk — line 265
# parameter: _items — line 265
# definition: pack — line 267
# parameter: _kwargs — line 267
# parameter: self — line 267
# definition: grid — line 270
# parameter: _kwargs — line 270
# parameter: self — line 270
# definition: grid_remove — line 273
# parameter: self — line 273
# definition: columnconfigure — line 276
# parameter: _args — line 276
# parameter: _kwargs — line 276
# parameter: self — line 276
# definition: add — line 279
# parameter: _args — line 279
# parameter: _kwargs — line 279
# parameter: self — line 279
# definition: theme_use — line 282
# parameter: _args — line 282
# parameter: self — line 282
# definition: configure — line 285
# parameter: _args — line 285
# parameter: kwargs — line 285
# parameter: self — line 285
# definition: heading — line 289
# parameter: _args — line 289
# parameter: _kwargs — line 289
# parameter: self — line 289
# definition: column — line 292
# parameter: _args — line 292
# parameter: _kwargs — line 292
# parameter: self — line 292
# definition: bind — line 295
# parameter: _args — line 295
# parameter: self — line 295
# definition: yview — line 298
# parameter: _args — line 298
# parameter: self — line 298
# definition: set — line 301
# parameter: _args — line 301
# parameter: self — line 301
# definition: state — line 304
# parameter: flags — line 304
# parameter: self — line 304
# variable: flag — line 306
# definition: invoke — line 312
# parameter: self — line 312
# definition: insert — line 318
# parameter: _parent — line 318
# parameter: _position — line 318
# parameter: iid — line 318
# parameter: self — line 318
# parameter: values — line 318
# definition: delete — line 322
# parameter: items — line 322
# parameter: self — line 322
# variable: item — line 324
# attribute: selected — line 326
# variable: item — line 326
# definition: get_children — line 328
# parameter: self — line 328
# definition: selection — line 332
# parameter: self — line 332
# definition: selection_set — line 336
# parameter: identity — line 336
# parameter: self — line 336
# attribute: selected — line 339
# definition: Text — line 342
# definition: delete — line 345
# parameter: _args — line 345
# parameter: self — line 345
# attribute: text — line 347
# definition: insert — line 349
# parameter: _position — line 349
# parameter: self — line 349
# parameter: text — line 349
# attribute: text — line 351
# definition: Root — line 354
# definition: __init__ — line 357
# parameter: self — line 357
# attribute: callbacks — line 359
# attribute: destroyed — line 359
# attribute: on_loop — line 360
# definition: title — line 362
# parameter: _args — line 362
# parameter: self — line 362
# definition: geometry — line 365
# parameter: _args — line 365
# parameter: self — line 365
# definition: minsize — line 368
# parameter: _args — line 368
# parameter: self — line 368
# definition: protocol — line 371
# parameter: _event — line 371
# parameter: callback — line 371
# parameter: self — line 371
# attribute: close_callback — line 373
# definition: after — line 375
# parameter: _delay — line 375
# parameter: callback — line 375
# parameter: self — line 375
# definition: destroy — line 379
# parameter: self — line 379
# attribute: destroyed — line 381
# definition: mainloop — line 383
# parameter: self — line 383
# variable: _ — line 387
# definition: presentation — line 395
# parameter: monkeypatch — line 395
# parameter: _parent — line 400
# variable: name — line 402
# variable: messages — line 416
# parameter: _kwargs — line 418
# parameter: args — line 418
# parameter: _kwargs — line 421
# parameter: args — line 421
# definition: app — line 427
# parameter: presentation — line 427
# parameter: tmp_path — line 427
# variable: state — line 429
# variable: root — line 430
# variable: window — line 431
# definition: settle — line 441
# parameter: window — line 441
# variable: deadline — line 443
# definition: test_next_page_and_selected_bookmark_restore_actual_saved_context — line 450
# parameter: app — line 450
# variable: index — line 454
# variable: first — line 460
# attribute: busy — line 469
# attribute: busy — line 472
# definition: test_real_controller_run_filter_detail_history_export_and_help — line 476
# parameter: app — line 477
# parameter: monkeypatch — line 477
# parameter: presentation — line 477
# parameter: tmp_path — line 477
# parameter: _kwargs — line 502
# variable: original — line 504
# variable: exported — line 506
# variable: path — line 507
# parameter: _kwargs — line 512
# definition: test_explicit_retention_confirmation_removes_only_selected_local_copy — line 518
# parameter: app — line 519
# parameter: monkeypatch — line 519
# parameter: tmp_path — line 519
# variable: exported — line 529
# variable: original — line 530
# parameter: _args — line 531
# parameter: _kwargs — line 531
# parameter: _args — line 534
# parameter: _kwargs — line 534
# variable: path — line 537
# attribute: busy — line 538
# attribute: busy — line 541
# definition: test_input_selection_cancel_busy_failure_and_literal_row_cap — line 544
# parameter: app — line 545
# parameter: monkeypatch — line 545
# parameter: tmp_path — line 545
# variable: name — line 548
# parameter: _kwargs — line 552
# parameter: _kwargs — line 557
# parameter: _kwargs — line 560
# variable: kind — line 562
# variable: value — line 566
# parameter: _kwargs — line 567
# attribute: busy — line 570
# attribute: busy — line 576
# attribute: current — line 583
# variable: index — line 583
# definition: test_close_retains_lock_until_actual_core_transaction_finishes — line 595
# parameter: app — line 596
# parameter: monkeypatch — line 596
# parameter: tmp_path — line 596
# variable: ready — line 599
# variable: release — line 599
# variable: actual — line 600
# definition: pause — line 602
# parameter: args — line 602
# variable: reopened — line 620
# definition: test_main_native_close_and_rejected_acceptance_paths — line 627
# parameter: monkeypatch — line 628
# parameter: presentation — line 628
# parameter: tmp_path — line 628
# variable: actual — line 631
# definition: create — line 633
# parameter: root — line 633
# parameter: state — line 633
# variable: window — line 635
# attribute: on_loop — line 636
# variable: profile — line 640
# variable: reopened — line 642
# variable: unknown — line 666
# END CODE MAP

import threading
import time
from types import SimpleNamespace

import pytest

from irkit import desktop as module
from irkit import desktop_project as project
from irkit.desktop_io import Rejected
from irkit.desktop_state import Workspace


class Variable:
    """Inert presentation variable; invokes the same registered GUI trace callbacks."""

    def __init__(self, value=""):
        """Keep a scalar control value and registered change callbacks."""
        self.value, self.callbacks = value, []

    def get(self):
        """Return the current presentation control value."""
        return self.value

    def set(self, value):
        """Change a control and exercise actual application rendering callbacks."""
        self.value = value
        for callback in self.callbacks:
            callback()

    def trace_add(self, _event, callback):
        """Retain the GUI's value-change handler."""
        self.callbacks.append(callback)


class Widget:
    """Minimal inert ttk presentation adapter; no core, storage or analysis output is mocked."""

    def __init__(self, *_args, **kwargs):
        """Retain properties, rows and command closures."""
        self.options, self.rows, self.selected = kwargs, {}, ()
        self.flags = set()
        self.tk = SimpleNamespace(call=lambda *_items: None)

    def pack(self, **_kwargs):
        """Accept presentation layout."""

    def grid(self, **_kwargs):
        """Accept presentation grid coordinates."""

    def grid_remove(self):
        """Accept operation-specific hidden controls."""

    def columnconfigure(self, *_args, **_kwargs):
        """Accept resize weights."""

    def add(self, *_args, **_kwargs):
        """Accept notebook/paned-window children."""

    def theme_use(self, *_args):
        """Accept native style selection."""

    def configure(self, *_args, **kwargs):
        """Retain updated widget options."""
        self.options.update(kwargs)

    def heading(self, *_args, **_kwargs):
        """Accept a literal table heading."""

    def column(self, *_args, **_kwargs):
        """Accept table sizing."""

    def bind(self, *_args):
        """Accept event registration; tests invoke actual handlers explicitly."""

    def yview(self, *_args):
        """Accept scroll requests."""

    def set(self, *_args):
        """Accept scrollbar position updates."""

    def state(self, flags):
        """Preserve disabled controls so a simulated click cannot bypass a busy guard."""
        for flag in flags:
            if flag.startswith("!"):
                self.flags.discard(flag[1:])
            else:
                self.flags.add(flag)

    def invoke(self):
        """Invoke the actual registered command unless the control is disabled."""
        if "disabled" not in self.flags:
            return self.options["command"]()
        return None

    def insert(self, _parent, _position, *, iid, values):
        """Retain exact rows inserted by real project rendering."""
        self.rows[iid] = values

    def delete(self, *items):
        """Remove rows and their selections like a real treeview."""
        for item in items:
            self.rows.pop(item, None)
        self.selected = tuple(item for item in self.selected if item in self.rows)

    def get_children(self):
        """Return displayed row identities."""
        return tuple(self.rows)

    def selection(self):
        """Return the current selected row identity."""
        return self.selected

    def selection_set(self, identity):
        """Select one existing row like a real single-selection control."""
        assert identity in self.rows
        self.selected = (identity,)


class Text(Widget):
    """Retain literal detail output without interpreting markup or executing event fields."""

    def delete(self, *_args):
        """Clear existing literal detail text."""
        self.text = ""

    def insert(self, _position, text):
        """Retain the exact rendered detail text."""
        self.text = text


class Root:
    """Deterministic presentation event queue; actual Tk mainloops are independently exercised by frozen acceptance."""

    def __init__(self):
        """Create a fresh owned presentation root."""
        self.callbacks, self.destroyed = [], False
        self.on_loop = None

    def title(self, *_args):
        """Accept window title."""

    def geometry(self, *_args):
        """Accept initial geometry."""

    def minsize(self, *_args):
        """Accept minimum geometry."""

    def protocol(self, _event, callback):
        """Keep the application's native close callback."""
        self.close_callback = callback

    def after(self, _delay, callback):
        """Queue the actual lifecycle callback without a platform display server."""
        self.callbacks.append(callback)

    def destroy(self):
        """Mark only this owned root as closed."""
        self.destroyed = True

    def mainloop(self):
        """Run the requested test lifecycle using real application callbacks."""
        if self.on_loop:
            self.on_loop()
        for _ in range(200):
            if self.destroyed:
                return
            self.callbacks.pop(0)()
        raise AssertionError("presentation lifecycle did not close")


@pytest.fixture
def presentation(monkeypatch):
    """Replace only OS presentation surfaces; real worker, core, SQLite and export code remain active."""
    monkeypatch.setattr(module.tk, "StringVar", Variable)
    monkeypatch.setattr(module.tk, "BooleanVar", Variable)
    monkeypatch.setattr(module.tk, "Tk", Root)
    monkeypatch.setattr(module.tk, "Toplevel", lambda _parent: Root())
    monkeypatch.setattr(module.tk, "Text", Text)
    for name in (
        "Frame",
        "Label",
        "Notebook",
        "Combobox",
        "Entry",
        "Button",
        "Checkbutton",
        "Panedwindow",
        "Treeview",
        "Scrollbar",
        "Style",
    ):
        monkeypatch.setattr(module.ttk, name, Widget)
    messages = []
    monkeypatch.setattr(
        module.messagebox, "showinfo", lambda *args, **_kwargs: messages.append(args)
    )
    monkeypatch.setattr(
        module.messagebox, "showerror", lambda *args, **_kwargs: messages.append(args)
    )
    return messages


@pytest.fixture
def app(tmp_path, presentation):
    """Build the actual workbench controller against an isolated real durable workspace."""
    state = Workspace(tmp_path / "profile", project.PRODUCT, project.ROOT)
    root = Root()
    window = module.Workbench(root, state)
    try:
        yield window
    finally:
        if window.worker_thread:
            window.worker_thread.join(10)
            assert not window.worker_thread.is_alive()
        state.close()


def settle(window):
    """Observe completion of one actual owned analysis; no retries or invented report values."""
    deadline = time.monotonic() + 10
    while window.busy and time.monotonic() < deadline:
        window.poll()
        time.sleep(0.005)
    assert not window.busy


def test_next_page_and_selected_bookmark_restore_actual_saved_context(app):
    """Navigation uses the completed original timeline, resets permission and does not silently run another read/write."""
    app.bookmark_selected()
    assert "Select a saved original" in app.status.get()
    for index in range(4):
        app.prepared.set(project.SCENARIOS[index])
        app.load_prepared()
        app.authorized.set(True)
        app.run_button.invoke()
        settle(app)
    first = app.state.files(4)
    app.review_button.invoke()
    assert app.values["cursor"].get() and app.mode.get() == project.MODES[2]
    assert app.authorized.get() is False and len(app.state.history()) == 4
    app.show(4)
    app.table.selection_set("0")
    app.bookmark_button.invoke()
    assert app.mode.get() == project.MODES[8] and app.values["line"].get() == "2"
    assert app.values["digest"].get() and not app.authorized.get()
    app.busy = True
    app.review_selected()
    app.bookmark_selected()
    app.busy = False
    assert app.state.files(4) == first


def test_real_controller_run_filter_detail_history_export_and_help(
    app, tmp_path, monkeypatch, presentation
):
    """Real core results drive controls, literal filters, exact private exports and history reopening."""
    app.export()
    assert "completed" in app.status.get()
    app.run_button.invoke()
    assert not app.busy and app.state.history() == []
    app.authorized.set(True)
    app.run_button.invoke()
    settle(app)
    assert app.selected_run == 1 and len(app.state.history()) == 1
    assert len(app.table.get_children()) > 0
    app.table.selection_set("0")
    app.inspect()
    assert "{" in app.details.text
    app.review_selected()
    assert "Select a saved original" in app.status.get()
    app.search.set("not-a-supported-record-never-present")
    assert app.table.get_children() == ()
    app.inspect()
    app.search.set("")
    app.history_table.selection_set("1")
    app.open_button.invoke()
    assert "without re-running" in app.status.get()
    monkeypatch.setattr(
        module.filedialog, "askdirectory", lambda **_kwargs: str(tmp_path)
    )
    original = app.state.files(1)
    app.export_button.invoke()
    exported = next(tmp_path.glob(project.PRODUCT + "-run-*"))
    assert {path.name: path.read_bytes() for path in exported.iterdir()} == original
    app.help()
    assert "plaintext" in presentation[-1][1]
    app.licenses()
    monkeypatch.setattr(
        module.filedialog, "askdirectory", lambda **_kwargs: str(tmp_path / "missing")
    )
    app.export()
    assert "unavailable" in app.status.get()


def test_explicit_retention_confirmation_removes_only_selected_local_copy(
    app, tmp_path, monkeypatch
):
    """Cancellation preserves data; confirmation deletes one exact DB bundle without touching a prior export."""
    app.remove_history()
    assert "Select" in app.status.get()
    app.review_selected()
    app.authorized.set(True)
    app.run_button.invoke()
    settle(app)
    app.history_table.selection_set("1")
    exported = app.state.export(1, tmp_path, project.PRODUCT)
    original = app.state.files(1)
    monkeypatch.setattr(module.messagebox, "askyesno", lambda *_args, **_kwargs: False)
    app.remove_button.invoke()
    assert app.state.files(1) == original
    monkeypatch.setattr(module.messagebox, "askyesno", lambda *_args, **_kwargs: True)
    app.remove_button.invoke()
    assert app.state.history() == [] and app.selected_run == 0
    assert {path.name: path.read_bytes() for path in exported.iterdir()} == original
    app.busy = True
    app.remove_history()
    assert "Wait" in app.status.get()
    app.busy = False


def test_input_selection_cancel_busy_failure_and_literal_row_cap(
    app, tmp_path, monkeypatch
):
    """Operator mistakes do not silently run a prepared fixture, overwrite results or defeat close semantics."""
    name = project.FIELDS[0][0]
    monkeypatch.setattr(
        module.filedialog,
        "askopenfilename",
        lambda **_kwargs: str(tmp_path / "authorized.json"),
    )
    monkeypatch.setattr(
        module.filedialog,
        "askopenfilenames",
        lambda **_kwargs: ("one.json", "two.json"),
    )
    monkeypatch.setattr(
        module.filedialog, "askdirectory", lambda **_kwargs: str(tmp_path)
    )
    for kind in ("file", "files", "directory"):
        app.authorized.set(True)
        app.choose(name, kind)
        assert app.authorized.get() is False
    value = app.values[name].get()
    monkeypatch.setattr(module.filedialog, "askopenfilename", lambda **_kwargs: "")
    app.choose(name, "file")
    assert app.values[name].get() == value
    app.busy = True
    app.choose(name, "file")
    app.load_prepared()
    app.open_history()
    app.run()
    assert app.state.history() == []
    app.busy = False
    app.load_prepared()
    app.mode.set("unsupported-operation")
    app.authorized.set(True)
    app.run()
    settle(app)
    assert "rejected" in app.status.get().lower() and app.state.history() == []
    app.current = {"bounded": [{"event": str(index)} for index in range(5001)]}
    app.view.set("bounded")
    app.render()
    assert len(app.table.get_children()) == 5000
    app.search.set('"5000"')
    assert len(app.table.get_children()) == 1
    app.exit()
    app.run()
    app.poll()
    assert app.root.destroyed and app.state.lock == -1


def test_close_retains_lock_until_actual_core_transaction_finishes(
    app, tmp_path, monkeypatch
):
    """An in-flight real analysis is drained rather than abandoned, force-killed or exposed to a second owner."""
    ready, release = threading.Event(), threading.Event()
    actual = project.analyze

    def pause(*args):
        """Control only scheduling; completion still invokes the actual project core and durable output."""
        ready.set()
        assert release.wait(5)
        return actual(*args)

    monkeypatch.setattr(project, "analyze", pause)
    app.authorized.set(True)
    app.run_button.invoke()
    assert ready.wait(3)
    app.exit()
    app.poll()
    assert not app.root.destroyed and app.busy
    with pytest.raises((Rejected, OSError)):
        Workspace(app.state.path, project.PRODUCT, project.ROOT)
    release.set()
    settle(app)
    assert app.root.destroyed and app.state.lock == -1
    reopened = Workspace(app.state.path, project.PRODUCT, project.ROOT)
    try:
        assert len(reopened.history()) == 1
    finally:
        reopened.close()


def test_main_native_close_and_rejected_acceptance_paths(
    tmp_path, presentation, monkeypatch
):
    """Normal startup never auto-analyzes; test flags cannot enter existing real-profile state or claim partial success."""
    actual = module.Workbench

    def create(root, state):
        """Use actual controls/controller; request the normal close callback at the start of the event loop."""
        window = actual(root, state)
        root.on_loop = window.exit
        return window

    monkeypatch.setattr(module, "Workbench", create)
    profile = tmp_path / "normal"
    assert module.main(["--profile", str(profile)]) == 0
    reopened = Workspace(profile, project.PRODUCT, project.ROOT)
    assert reopened.history() == []
    reopened.close()
    with pytest.raises(SystemExit):
        module.main(["--acceptance-output", str(tmp_path / "output")])
    with pytest.raises(SystemExit):
        module.main(["--acceptance-reopen"])
    assert (
        module.main(
            ["--profile", str(profile), "--acceptance-output", str(tmp_path / "output")]
        )
        == 2
    )
    assert (
        module.main(
            [
                "--profile",
                str(tmp_path / "synthetic"),
                "--acceptance-output",
                str(tmp_path / "new-output"),
            ]
        )
        == 2
    )
    unknown = tmp_path / "unknown"
    unknown.mkdir()
    (unknown / "keep").write_bytes(b"unchanged")
    assert module.main(["--profile", str(unknown)]) == 2
    assert (unknown / "keep").read_bytes() == b"unchanged"
    assert presentation and "No saved evidence was reset" in presentation[-1][1]
