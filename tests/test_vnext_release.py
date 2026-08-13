import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V600 = ROOT / "reports/vnext_600_regression.json"
PRM = ROOT / "experiments/prm800k_audit/results/cross_source_gap_pilot_vnext_1.0.0_summary.json"
TENK = ROOT / "data/vnext_10k"


def rows(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        yield from (json.loads(line) for line in stream if line.strip())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_vnext_600_is_complete_and_refusal_free():
    report = json.loads(V600.read_text())
    assert report["authority"] == {
        "hml_semantic_commit": "68178f07784d2a17a9aed9c4dedbea9c740c97a0",
        "contract_version": "vnext-translation-contract-1.0.0",
    }
    assert report["source"] ["problems"] == 600
    assert report["source"] ["transitions"] == 3978
    assert report["source_transition_outcomes"] == {"FAITHFUL": 3978}
    assert report["root_refusals"] == []
    assert report["failures"] == []
    assert report["implicit_logical_steps"]["inserted"] == 16
    assert report["implicit_logical_steps"]["missing"] == []
    assert report["representations"]["leakage_audit"] == "PASS"
    assert set(report["representations"]["counts"].values()) == {4127}
    metrics = report["vnext_600_metrics"]
    assert metrics["semantic_refusals"] == metrics["corpus_information_refusals"] == 0
    assert metrics["parser_failures"] == metrics["verifier_failures"] == metrics["round_trip_failures"] == 0


def test_exact_prm1k_regression_preserves_label_epistemics():
    report = json.loads(PRM.read_text())
    assert report["records"] == 1000
    assert report["source_validation"] == "1000/1000 exact"
    assert report["unique_source_problems"] == 858
    assert report["unique_source_trajectories"] == 907
    assert report["previously_current_known_core_gap"] == 693
    assert report["previously_core_now_represented"] == 670
    assert report["previously_core_corpus_information_refusals"] == 23
    assert report["remaining_candidate_related_core_gap_rows"] == 0
    assert report["remaining_approximation_related_core_gap_rows"] == 0
    assert report["new_recurring_core_semantic_candidates"] == 0
    assert report["process_label_policy"].endswith("never mathematical evidence.")


def test_10k_manifest_files_hashes_and_composition():
    manifest = json.loads((TENK / "manifest.json").read_text())
    assert manifest["record_count"] == 10000
    assert manifest["hml_semantic_commit"] == "68178f07784d2a17a9aed9c4dedbea9c740c97a0"
    assert manifest["contract_version"] == "vnext-translation-contract-1.0.0"
    assert manifest["source_counts"] == {
        "AMPS": 1000, "LEAN_DOJO": 4000, "MATH": 2000,
        "PRM800K": 2000, "SYNTHETIC_HARD_TAIL": 1000,
    }
    assert sum(manifest["split_counts"].values()) == 10000
    assert set(manifest["representation_counts"].values()) == {10000}
    assert manifest["representation_parity"] == "10000/10000 PASS"
    assert manifest["leakage_audit"] == "10000/10000 PASS"
    assert manifest["deduplication"]["parent_group_split_leakage"] == "PASS"
    assert manifest["deduplication"]["miniF2F_ProofNet_bulk_training"] is False
    for relative, expected in manifest["files"].items():
        path = TENK / relative
        assert path.stat().st_size == expected["bytes"]
        assert sha(path) == expected["sha256"]


def test_10k_parent_splits_do_not_leak_and_records_are_unique():
    seen_ids = set()
    group_split = {}
    counts = {}
    for split in ("train", "dev", "test"):
        split_rows = list(rows(TENK / f"{split}.jsonl.gz"))
        counts[split] = len(split_rows)
        for item in split_rows:
            assert item["record_id"] not in seen_ids
            seen_ids.add(item["record_id"])
            group = item["parent_group_sha256"]
            assert group_split.setdefault(group, split) == split
            assert item["split"] == split
            assert item["representation_parity"] == item["leakage_check"] == "PASS"
    assert len(seen_ids) == 10000
    assert counts == json.loads((TENK / "manifest.json").read_text())["split_counts"]


def test_10k_safe_views_are_matched_and_exclude_forbidden_action_fields():
    ids_by_arm = {}
    for arm in ("HML_LINEAR", "HML_TREE", "AST", "STRUCTURED_NEUTRAL"):
        arm_ids = []
        for split in ("train", "dev", "test"):
            for item in rows(TENK / "views" / arm / f"{split}.jsonl.gz"):
                arm_ids.append(item["record_id"])
                if arm == "STRUCTURED_NEUTRAL":
                    assert "state_after" not in item["input"]
                    assert set(item["input"]["action"]).isdisjoint(
                        {"summary", "output_id", "source", "state_after", "target_delta"}
                    )
                elif arm in {"HML_LINEAR", "HML_TREE"}:
                    action = item["input"].rsplit("\nACTION ", 1)[1]
                    assert all(token not in action for token in (
                        '"summary"', '"output_id"', '"source"', '"state_after"', '"target_delta"'
                    ))
        assert len(arm_ids) == len(set(arm_ids)) == 10000
        ids_by_arm[arm] = set(arm_ids)
    assert len({frozenset(value) for value in ids_by_arm.values()}) == 1


def test_snapshots_are_exact_nested_prefixes():
    snapshots = json.loads((TENK / "snapshots.json").read_text())
    sizes = [100, 250, 1000, 5000, 10000]
    prior = set()
    for size in sizes:
        ids = snapshots[str(size)]["record_ids"]
        assert len(ids) == len(set(ids)) == size
        assert prior < set(ids) if prior else True
        prior = set(ids)
        assert sum(snapshots[str(size)]["source_counts"].values()) == size
        assert snapshots[str(size)]["task_counts"]["COMPREHENSION"] == size
