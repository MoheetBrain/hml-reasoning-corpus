import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "experiments" / "prm800k_audit" / "audit_prm800k.py"
SPEC = importlib.util.spec_from_file_location("audit_prm800k", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_state_proxy_uses_only_prior_selected_text():
    row = {
        "question": {"problem": "Find x", "ground_truth_answer": "1"},
        "label": {
            "finish_reason": "solution",
            "steps": [
                {"completions": [{"text": "A", "rating": 1, "flagged": None}], "chosen_completion": 0, "human_completion": None},
                {"completions": [{"text": "B", "rating": -1, "flagged": None}, {"text": "C", "rating": 1, "flagged": None}], "chosen_completion": 1, "human_completion": None},
            ],
        },
    }
    records = list(MODULE.candidate_records("phase1", "test", 1, row, {}))
    assert records[0]["preceding_state_proxy"] == []
    assert records[1]["preceding_state_proxy"] == [{"step_position_1_based": 1, "origin": "model_completion", "text": "A"}]
    assert records[2]["preceding_state_proxy"] == records[1]["preceding_state_proxy"]


def test_frozen_output_cardinalities_and_state_proxy_warning():
    root = ROOT / "experiments" / "prm800k_audit"
    deep = [json.loads(line) for line in (root / "samples" / "deep_sample.jsonl").read_text().splitlines()]
    decisions = [json.loads(line) for line in (root / "samples" / "phase1_decision_points.jsonl").read_text().splitlines()]
    counts = {rating: sum(row["rating"] == rating for row in deep) for rating in (-1, 0, 1)}
    assert counts == {-1: 500, 0: 250, 1: 250}
    assert len(decisions) == 200
    assert all(row["record_type"] == "STATE_PROXY_CANDIDATE" for row in deep)
    assert all("not a canonical" in row["state_proxy_warning"] for row in deep)


def test_every_sampled_candidate_has_one_annotation():
    root = ROOT / "experiments" / "prm800k_audit"
    deep = [json.loads(line) for line in (root / "samples" / "deep_sample.jsonl").read_text().splitlines()]
    expected = {row["candidate_id"] for row in deep}
    actual = set()
    for name in ("minus_one_audit.jsonl", "zero_audit.jsonl", "plus_one_audit.jsonl"):
        actual.update(json.loads(line)["candidate_id"] for line in (root / "annotations" / name).read_text().splitlines())
    assert actual == expected


def test_source_manifest_matches_mission_commit():
    manifest = json.loads((ROOT / "experiments" / "prm800k_audit" / "results" / "source_manifest.json").read_text())
    assert manifest["source_commit"] == "7ecc794703b2877f63226f2477a49b34f9b25163"
    assert len(manifest["source_files"]) == 4


def test_manual_spotcheck_is_explicitly_non_prevalence():
    root = ROOT / "experiments" / "prm800k_audit"
    audit = json.loads((root / "annotations" / "manual_spotcheck.json").read_text())
    assert audit["status"] == "INDEPENDENT_MANUAL_SPOTCHECK_NOT_A_PREVALENCE_SAMPLE"
    assert len(audit["records"]) == 12
    assert "prevalence estimator" in audit["conclusion"]
