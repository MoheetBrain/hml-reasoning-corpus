from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

from scripts.reasoning_layer_discovery.semantic_extractor import (
    HISTORY_WINDOW,
    extract_reasoning_state,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/reasoning_layer_discovery"


def load(path: str):
    return json.loads((OUT / path).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def test_stage_integrity_and_status():
    assert load("DISCOVERY_STAGE_INTEGRITY.json")["result"] == "PASS"
    assert load("STAGE_STATUS.json") == {
        "integrity": "PASS",
        "status": "SEMANTIC_TEST_READY",
        "training_authorized_in_this_stage": False,
    }


def test_stage_manifest_hashes_every_payload():
    manifest = load("DISCOVERY_STAGE_MANIFEST.json")
    assert manifest["result"] == "PASS"
    for name, metadata in manifest["files"].items():
        path = ROOT / name if name.startswith(("scripts/", "tests/")) else OUT / name
        assert path.stat().st_size == metadata["bytes"]
        assert sha256(path) == metadata["sha256"]


def test_fresh_holdouts_are_sealed_and_disjoint():
    manifest = load("FRESH_HOLDOUT_MANIFEST.json")
    assert manifest["integrity"] == "PASS"
    assert manifest["holdouts"]["FRESH_FINAL_A"]["records"] == 3000
    assert manifest["holdouts"]["FRESH_FINAL_B"]["records"] == 3000
    assert all(manifest["exclusions"][key] for key in (
        "zero_parent_overlap_with_all_previous_hml50k_and_vnext",
        "zero_exact_state_overlap_with_previous_hml50k",
        "zero_parent_overlap_a_vs_b",
        "zero_exact_state_overlap_a_vs_b",
    ))
    assignment = OUT / manifest["sealed_assignment_file"]["path"]
    assert sha256(assignment) == manifest["sealed_assignment_file"]["sha256"]
    with gzip.open(assignment, "rt", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle]
    assert len(rows) == 6000
    assert not ({x["parent_id"] for x in rows if x["holdout"] == "FRESH_FINAL_A"} &
                {x["parent_id"] for x in rows if x["holdout"] == "FRESH_FINAL_B"})
    assert all("action" not in row and "gold_label" not in row for row in rows)


def test_failure_atlas_has_every_discovery_row():
    with (OUT / "reasoning_failure_rows.jsonl").open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle]
    assert len(rows) == 3000
    assert len({row["record_id"] for row in rows}) == 3000
    assert sum(row["disagreement_category"] == "BOTH_WRONG" for row in rows) == 310
    assert all(row["actual_failed_or_invalid_actions_available"] is False for row in rows)


def test_v1_schema_is_precise_and_decomposable():
    schema = load("REASONING_STATE_SCHEMA_V1.json")
    expected = {
        "schema_version", "active_goal", "open_goals", "local_dependencies", "active_scope",
        "trajectory_position", "recent_actions", "recent_deltas", "progress_summary",
    }
    assert set(schema["required"]) == expected
    assert schema["additionalProperties"] is False
    assert schema["properties"]["recent_actions"]["maxItems"] == HISTORY_WINDOW
    assert schema["x-scientific-constraints"]["uses_gold_or_future_action"] is False


def test_extractor_uses_only_current_state_and_bounded_prefix():
    prior = [{
        "state_before": "x : Nat\n⊢ x = x",
        "action": "rfl",
        "state_after": "no goals",
    }] * (HISTORY_WINDOW + 3)
    state = extract_reasoning_state("case left\nx : Nat\nh : x = x\n⊢ x = x", prior)
    assert len(state["recent_actions"]) == HISTORY_WINDOW
    assert len(state["recent_deltas"]) == HISTORY_WINDOW
    assert state["trajectory_position"]["steps_completed"] == HISTORY_WINDOW + 3
    assert state["active_scope"] == {"case_label": "left", "source_explicit": True}
    assert "gold" not in json.dumps(state).lower()
