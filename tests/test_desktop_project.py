"""Real private-case GUI adapters: exact original bytes, UTC pagination and minimized handoffs. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: state — line 115
# parameter: tmp_path — line 115
# variable: value — line 117
# definition: run — line 124
# parameter: changes — line 124
# parameter: index — line 124
# parameter: state — line 124
# parameter: tmp_path — line 124
# variable: parameters — line 126
# variable: stage — line 127
# variable: files — line 129
# variable: kind — line 129
# variable: summary — line 129
# variable: identity — line 130
# definition: collected — line 134
# parameter: state — line 134
# parameter: tmp_path — line 134
# variable: index — line 136
# definition: test_create_collect_preserves_both_original_bytes_and_deduplicates — line 141
# parameter: state — line 141
# parameter: tmp_path — line 141
# variable: case — line 143
# variable: connection — line 145
# variable: observed — line 146
# variable: name — line 147
# variable: original — line 148
# variable: before — line 150
# definition: test_bound_keyset_cursor_pages_exact_utc_events_and_rejects_stale_context — line 158
# parameter: state — line 159
# parameter: tmp_path — line 159
# variable: case — line 162
# variable: _ — line 163
# variable: files — line 163
# variable: identity — line 163
# variable: first — line 164
# variable: row — line 165
# variable: row — line 169
# variable: all_rows — line 170
# variable: remaining — line 171
# variable: parameters — line 172
# variable: _ — line 173
# variable: files — line 173
# variable: identity — line 173
# variable: value — line 174
# variable: all_rows — line 176
# variable: row — line 177
# definition: test_private_checkpoint_bookmark_note_omission_and_minimized_export — line 190
# parameter: state — line 191
# parameter: tmp_path — line 191
# variable: case — line 194
# variable: _ — line 195
# variable: files — line 195
# variable: identity — line 195
# variable: row — line 196
# variable: parameters — line 197
# variable: _ — line 199
# variable: pin_files — line 199
# variable: pin — line 200
# variable: _ — line 205
# variable: handoff — line 205
# variable: result — line 206
# variable: value — line 208
# variable: _ — line 216
# variable: minimized — line 216
# variable: _ — line 221
# variable: template_files — line 221
# variable: template — line 224
# variable: source — line 234
# variable: _ — line 236
# variable: imported — line 236
# definition: test_existing_cli_case_opaque_input_custody_and_invalid_parameters — line 259
# parameter: state — line 259
# parameter: tmp_path — line 259
# variable: external — line 261
# variable: source — line 264
# variable: _ — line 266
# variable: files — line 266
# variable: digest — line 269
# variable: _ — line 270
# variable: assertion — line 270
# variable: before — line 280
# variable: changes — line 281
# definition: test_managed_names_cannot_escape_or_use_reserved_windows_devices — line 300
# parameter: alias — line 300
# parameter: state — line 300
# definition: test_case_capacity_history_capacity_and_unknown_prepared_scenario — line 306
# parameter: state — line 306
# parameter: tmp_path — line 306
# variable: index — line 308
# variable: connection — line 314
# variable: index — line 319
# definition: test_hidden_retained_inputs_do_not_change_selected_operation_and_oversize_precedes_mutation — line 327
# parameter: state — line 328
# parameter: tmp_path — line 328
# variable: _ — line 331
# variable: files — line 331
# END CODE MAP

import hashlib
import json
from contextlib import closing

import pytest

from irkit import desktop_project as project
from irkit.contracts import EvidenceError
from irkit.desktop_io import Rejected, json_value
from irkit.desktop_state import Workspace
from irkit.store import Case


@pytest.fixture
def state(tmp_path):
    """Own a disposable native-profile marker and real SQLite history, never a user's existing case."""
    value = Workspace(tmp_path / "profile", project.PRODUCT, project.ROOT)
    try:
        yield value
    finally:
        value.close()


def run(state, tmp_path, index=0, **changes):
    """Run original core methods from actual parameter maps and retain the exact completed output bundle."""
    parameters = project.scenario(project.SCENARIOS[index]) | changes
    stage = tmp_path / ("stage-" + str(len(state.history())))
    stage.mkdir(exist_ok=True)
    kind, summary, files = project.analyze(state, parameters, stage)
    identity = state.save(kind, summary, parameters, files)
    return identity, files, summary


def collected(state, tmp_path):
    """Use explicit Create/Collect operations to preserve both unsorted source formats in one real case."""
    for index in range(3):
        run(state, tmp_path, index)
    return Case(state.path / "cases/fictional-access-review")


def test_create_collect_preserves_both_original_bytes_and_deduplicates(state, tmp_path):
    """The GUI has no synthetic success substitution: its case holds the exact selected JSONL and CSV bytes."""
    case = collected(state, tmp_path)
    assert case.verify()["events"] == 5
    with case.connection() as connection:
        observed = dict(connection.execute("SELECT digest,raw FROM evidence"))
    for name in ("access-review.jsonl", "service-change.csv"):
        original = (project.ROOT / "examples" / name).read_bytes()
        assert observed[hashlib.sha256(original).hexdigest()] == original
    before = case.verify()
    run(state, tmp_path, 1)
    assert case.verify() == before
    with pytest.raises(FileExistsError):
        run(state, tmp_path, 0)
    assert len(state.history()) == 4


def test_bound_keyset_cursor_pages_exact_utc_events_and_rejects_stale_context(
    state, tmp_path
):
    """Two-event pages resolve all five records once; an altered filter or newly committed custody head invalidates a cursor."""
    case = collected(state, tmp_path)
    identity, files, _ = run(state, tmp_path, 3)
    first = json_value(files["result.json"])
    assert [row["utc"] for row in first["records"]] == [
        "2026-10-10T16:00:00.000000Z",
        "2026-10-10T16:00:30.000000Z",
    ]
    assert [row["line"] for row in first["records"]] == [2, 3]
    all_rows = first["records"][:]
    for remaining in (True, False):
        parameters = project.prepare_selected(state, identity)
        identity, files, _ = run(state, tmp_path, 3, **parameters)
        value = json_value(files["result.json"])
        assert value["more_available"] is remaining and value["filter_matches"] == 5
        all_rows += value["records"]
    assert len({(row["evidence_sha256"], row["line"]) for row in all_rows}) == 5
    assert all_rows[-1]["kind"] == "alert"
    with pytest.raises(Rejected):
        project.next_page(files)
    with pytest.raises(Rejected, match="stale"):
        run(state, tmp_path, 3, cursor=json.dumps(first["next_cursor"]), kind="alert")
    case.record(
        all_rows[0]["evidence_sha256"], "review", "analyst-b", "2026-10-10T16:04:00Z"
    )
    with pytest.raises(Rejected, match="stale"):
        run(state, tmp_path, 3, cursor=json.dumps(first["next_cursor"]))


def test_private_checkpoint_bookmark_note_omission_and_minimized_export(
    state, tmp_path
):
    """A private selected-source record becomes a pseudonymized handoff without leaking its note, operator, hashes or identity."""
    case = collected(state, tmp_path)
    identity, files, _ = run(state, tmp_path, 3)
    row = json_value(files["result.json"])["records"][0]
    parameters = project.prepare_selected(state, identity, row)
    assert parameters["mode"] == project.MODES[8] and parameters["line"] == "2"
    _, pin_files, _ = run(state, tmp_path, 5)
    pin = tmp_path / "independent-test-pin.json"
    pin.write_bytes(pin_files["private-checkpoint.json"])
    parameters.update(
        checkpoint=str(pin), note="PRIVATE-NOTE-SENTINEL", operator="private-operator"
    )
    _, handoff, _ = run(state, tmp_path, **parameters)
    result = json_value(handoff["handoff.json"])
    assert len(result["timeline"]) == 1 and result["timeline"][0]["line"] == 2
    for value in handoff.values():
        assert (
            b"PRIVATE-NOTE-SENTINEL" not in value and b"private-operator" not in value
        )
        assert (
            row["evidence_sha256"].encode() not in value
            and row["actor"].encode() not in value
        )
    _, minimized, _ = run(state, tmp_path, 6, checkpoint=str(pin))
    assert set(minimized) == {"report.json", "report.html", "timeline.csv"}
    assert len(json_value(minimized["report.json"])["timeline"]) == 5
    with pytest.raises(Rejected):
        project.prepare_selected(state, len(state.history()), result["timeline"][0])
    _, template_files, _ = run(
        state, tmp_path, 4, mode=project.MODES[7], checkpoint=str(pin)
    )
    template = json_value(template_files["private-bookmarks.json"])
    template["entries"] = [
        {
            "evidence_sha256": row["evidence_sha256"],
            "line": 2,
            "operator": "analyst-local",
            "tag": "key-event",
            "note": "Private external selection",
        }
    ]
    source = tmp_path / "private-selection.json"
    source.write_text(json.dumps(template))
    _, imported, _ = run(
        state,
        tmp_path,
        4,
        mode=project.MODES[8],
        selections=str(source),
        checkpoint=str(pin),
    )
    assert json_value(imported["handoff.json"])["timeline"][0]["tag"] == "key-event"
    case.record(
        row["evidence_sha256"], "review", "analyst-local", "2026-10-10T16:05:00Z"
    )
    with pytest.raises(EvidenceError, match="snapshot"):
        run(
            state,
            tmp_path,
            4,
            mode=project.MODES[8],
            selections=str(source),
            checkpoint=str(pin),
        )


def test_existing_cli_case_opaque_input_custody_and_invalid_parameters(state, tmp_path):
    """The native workflow accepts an original CLI case and opaque bytes while rejecting invented commands, bad limits and pins."""
    external = Case.create(
        tmp_path / "external", "external-analyst", "2026-10-10T16:00:00Z"
    )
    source = tmp_path / "evidence.bin"
    source.write_bytes(bytes(range(256)))
    _, files, _ = run(
        state, tmp_path, 1, case=str(external.root), input=str(source), format="opaque"
    )
    digest = json_value(files["result.json"])["collected_sha256"]
    _, assertion, _ = run(
        state,
        tmp_path,
        4,
        case=str(external.root),
        mode=project.MODES[4],
        digest=digest,
        action="handoff",
    )
    assert json_value(assertion["result.json"])["verification"]["seq"] == 3
    before = external.verify()
    for changes in (
        {"mode": "collect entire host"},
        {"limit": "0"},
        {"limit": "NaN"},
        {"limit": "1001"},
        {"limit": "1.0"},
        {"cursor": "[]"},
        {"cursor": json.dumps({"case_id": "wrong"})},
        {"checkpoint": str(source)},
    ):
        with pytest.raises((Rejected, EvidenceError, OSError)):
            run(state, tmp_path, 3, case=str(external.root), **changes)
    assert external.verify() == before
    assert project.views(files) and project.cells({"line": 1, "utc": "test"})


@pytest.mark.parametrize(
    "alias", ["../escape", "CON", "con", "aux", "com1", "", "space name", "x" * 41]
)
def test_managed_names_cannot_escape_or_use_reserved_windows_devices(state, alias):
    """The default application cannot create a case at a traversal/device path."""
    with pytest.raises(Rejected):
        project.case_path(state, {"alias": alias}, create=True)


def test_case_capacity_history_capacity_and_unknown_prepared_scenario(state, tmp_path):
    """Finite local limits refuse before creating an additional case or silently deleting retained originals."""
    for index in range(8):
        run(state, tmp_path, alias="case-" + str(index))
    with pytest.raises(Rejected, match="eight"):
        run(state, tmp_path, alias="case-nine")
    with pytest.raises(Rejected):
        project.scenario("live incident response")
    with closing(state.connect()) as connection, connection:
        connection.executemany(
            "INSERT INTO run VALUES(?,?,?,?,?)",
            [
                (index, "now", "inert", "capacity fixture", "{}")
                for index in range(9, 21)
            ],
        )
    with pytest.raises(Rejected, match="history"):
        run(state, tmp_path, 1)
    assert len(list((state.path / "cases").iterdir())) == 8


def test_hidden_retained_inputs_do_not_change_selected_operation_and_oversize_precedes_mutation(
    state, tmp_path
):
    """Switching away from an external case/bookmark must not reuse hidden paths or create an unrecorded case after text-limit failure."""
    _, files, _ = run(
        state,
        tmp_path,
        case=str(tmp_path / "not-selected-case"),
        checkpoint=str(tmp_path / "not-selected-pin"),
        cursor="bad hidden cursor",
    )
    assert json_value(files["result.json"])["verification"]["files"] == 0
    with pytest.raises(Rejected, match="parameter"):
        run(state, tmp_path, alias="must-not-exist", note="x" * (512 * 1024 + 1))
    assert not (state.path / "cases/must-not-exist").exists()
