"""Real hostile SQLite case-admission and bounded-query regressions; no original host evidence. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_imported_case_view_is_rejected_before_application_query — line 35
# parameter: case — line 35
# parameter: table — line 35
# variable: connection — line 37
# variable: name — line 38
# definition: test_connection_bounds_values_before_fetch_and_closes_on_failure — line 52
# parameter: case — line 52
# parameter: monkeypatch — line 52
# variable: connection — line 55
# variable: connection — line 60
# definition: test_expensive_sql_is_interrupted_by_actual_connection_vm_budget — line 64
# parameter: case — line 64
# parameter: monkeypatch — line 64
# variable: connection — line 69
# definition: test_private_initialization_cannot_bypass_existing_case_admission — line 76
# parameter: case — line 76
# variable: before — line 78
# definition: test_virtual_table_cannot_hide_behind_sql_comments — line 92
# parameter: case — line 92
# variable: connection — line 94
# END CODE MAP

import sqlite3
from contextlib import closing

import pytest

from irkit import store
from irkit.contracts import EvidenceError


@pytest.mark.parametrize("table", ["metadata", "evidence", "events", "custody"])
def test_imported_case_view_is_rejected_before_application_query(case, table):
    """An attacker-controlled recursive view is not an ordinary case table, even without an external pin."""
    with closing(sqlite3.connect(case.database)) as connection, connection:
        for (name,) in connection.execute(
            "SELECT name FROM sqlite_schema WHERE type='trigger'"
        ).fetchall():
            connection.execute('DROP TRIGGER "' + name + '"')
        connection.execute('DROP TABLE "' + table + '"')
        connection.execute(
            'CREATE VIEW "'
            + table
            + '" AS WITH RECURSIVE x(a) AS (VALUES(1) UNION ALL SELECT a+1 FROM x) SELECT * FROM x'
        )
    with pytest.raises(EvidenceError, match="case_schema"):
        case.verify()


def test_connection_bounds_values_before_fetch_and_closes_on_failure(case, monkeypatch):
    """A forged oversized row cannot be materialized by an imported-case read, and its connection does not retain a lock."""
    monkeypatch.setattr(store, "MAX_FILE", 32)
    with closing(sqlite3.connect(case.database)) as connection, connection:
        connection.execute("DROP TRIGGER metadata_no_update")
        connection.execute("UPDATE metadata SET case_id=?", ("x" * 100000,))
    with pytest.raises(EvidenceError, match="case_integrity"):
        case.verify()
    with closing(sqlite3.connect(case.database, timeout=0.1)) as connection:
        connection.execute("BEGIN EXCLUSIVE")


def test_expensive_sql_is_interrupted_by_actual_connection_vm_budget(case, monkeypatch):
    """The admission bound also covers an expensive query on a real connection, independent of table-type validation."""
    monkeypatch.setattr(store, "VM_STEPS", 2000)
    with (
        pytest.raises(sqlite3.OperationalError, match="interrupted"),
        case.connection() as connection,
    ):
        connection.execute(
            "WITH RECURSIVE x(a) AS (VALUES(1) UNION ALL SELECT a+1 FROM x WHERE a<10000000) SELECT sum(a) FROM x"
        ).fetchone()


def test_private_initialization_cannot_bypass_existing_case_admission(case):
    """Initialization is exclusive to an empty new database; normal existing cases and original verification still work."""
    before = case.verify()
    with (
        pytest.raises(EvidenceError, match="case_initialization"),
        case.connection(write=True, _initialize=True),
    ):
        pass
    assert case.verify() == before
    with (
        pytest.raises(EvidenceError, match="case_initialization"),
        case.connection(_initialize=True),
    ):
        pass


def test_virtual_table_cannot_hide_behind_sql_comments(case):
    """SQLite's own table classification rejects virtual application tables without trusting DDL spelling."""
    with closing(sqlite3.connect(case.database)) as connection, connection:
        connection.execute("DROP TRIGGER metadata_no_update")
        connection.execute("DROP TRIGGER metadata_no_delete")
        connection.execute("DROP TABLE metadata")
        connection.execute(
            "CREATE /* spelling is not authority */ VIRTUAL TABLE metadata USING fts5(case_id,pseudonym_key)"
        )
    with pytest.raises(EvidenceError, match="case_schema"):
        case.verify()
