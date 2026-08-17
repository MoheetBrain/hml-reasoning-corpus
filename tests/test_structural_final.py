import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MISSION = ROOT / "data" / "hml_structural_final"


def test_raw_census_conservation_and_fresh_depth_bins():
    report = json.loads((MISSION / "SOURCE_AUDIT" / "lean_raw_structural_census.json").read_text())
    counts = report["counts"]
    assert counts["transitions"] == 259580
    assert counts["old_history_excluded"] + counts["fresh_transitions"] == counts["transitions"]
    assert counts["fresh_transitions"] == counts["exact_before_action_after"] == 216623
    assert sum(report["fresh_proof_depth_distribution"].values()) == 216623
    assert report["fresh_trajectory_length"]["count"] == 57874
    assert sum(report["fresh_trajectory_length"]["bins"].values()) == 57874
    assert report["fresh_trajectory_length"]["multi_step_count"] == 36698


def test_canonical_census_conservation():
    report = json.loads((MISSION / "SOURCE_AUDIT" / "lean_structural_census.json").read_text())
    counts = report["counts"]
    assert counts["records"] == 241265
    assert counts["old_history_excluded"] + counts["fresh_records"] == counts["records"]
    assert report["source_sha256"] == "8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869"


def test_refusal_has_no_fake_rung_or_model_view():
    rungs = json.loads((MISSION / "MANIFESTS" / "rung_availability.json").read_text())
    assert rungs["verdict"] == "INSUFFICIENT_STRUCTURAL_DATA"
    assert rungs["admitted_records"] == 0
    assert set(rungs["rungs"].values()) == {"UNAVAILABLE"}
    forbidden = ["FULL", "STRUCT_2K", "STRUCT_5K", "STRUCT_10K", "STRUCT_30K", "STRUCT_50K"]
    assert not any((MISSION / name).exists() for name in forbidden)


def test_manifest_hashes_and_sidecar():
    manifest_path = MISSION / "STRUCTURAL_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    assert manifest["verdict"] == "INSUFFICIENT_STRUCTURAL_DATA"
    assert manifest["selection"]["admitted_records"] == 0
    for item in manifest["files"]:
        path = ROOT / item["path"]
        assert path.stat().st_size == item["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
    expected = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    assert (MISSION / "STRUCTURAL_MANIFEST.sha256").read_text() == f"{expected}  STRUCTURAL_MANIFEST.json\n"


def test_mission_json_uses_literal_unicode():
    escaped = re.compile(rb"\\u[0-9a-fA-F]{4}")
    for path in MISSION.rglob("*.json"):
        if path.name == "STRUCTURAL_MANIFEST.json":
            continue
        assert escaped.search(path.read_bytes()) is None, path
