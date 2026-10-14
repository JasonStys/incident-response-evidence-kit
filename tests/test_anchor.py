"""Prove the difference between internal consistency and an independently retained prefix. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_consistent_rewrite_requires_external_pin — line 30
# parameter: attack — line 30
# parameter: case — line 30
# parameter: sample — line 30
# variable: digest — line 32
# variable: before — line 34
# variable: checkpoint — line 35
# variable: name — line 35
# variable: trigger — line 36
# variable: connection — line 37
# variable: trigger_sql — line 38
# variable: _ — line 43
# variable: encoded — line 43
# variable: previous — line 43
# variable: seq — line 43
# variable: payload — line 46
# END CODE MAP

import json

import pytest
from conftest import NOW

from irkit.contracts import EvidenceError, canonical, sha


@pytest.mark.parametrize("attack", ["rewrite", "truncate"])
def test_consistent_rewrite_requires_external_pin(case, sample, attack):
    """Privileged rewrites can look internally consistent; an original external pin still rejects them."""
    digest = case.collect(sample, "jsonl", "analyst-a", "host-demo", NOW)
    case.record(digest, "review", "analyst-b", NOW)
    before = case.verify()
    checkpoint = {name: before[name] for name in ("schema", "case_id", "seq", "head")}
    trigger = "custody_no_update" if attack == "rewrite" else "custody_no_delete"
    with case.connection(write=True) as connection:
        trigger_sql = connection.execute(
            "SELECT sql FROM sqlite_schema WHERE name=?", (trigger,)
        ).fetchone()[0]
        connection.execute("DROP TRIGGER " + trigger)
        if attack == "rewrite":
            seq, encoded, previous, _ = connection.execute(
                "SELECT * FROM custody WHERE seq=3"
            ).fetchone()
            payload = json.loads(encoded)
            payload["operator"] = "different-analyst"
            connection.execute(
                "UPDATE custody SET payload=?,head=? WHERE seq=3",
                (canonical(payload).decode(), sha(canonical([seq, previous, payload]))),
            )
        else:
            connection.execute("DELETE FROM custody WHERE seq=3")
        connection.execute(trigger_sql)
    # Explicitly demonstrate the limit, rather than pretending a same-disk hash chain is authenticated.
    assert not case.verify()["anchored"]
    with pytest.raises(EvidenceError, match="checkpoint_mismatch"):
        case.verify(checkpoint)
