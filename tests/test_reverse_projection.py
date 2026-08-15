import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

from scripts.vnext.build_reverse_projection import action_from_ast, action_from_hml


ROOT = Path(__file__).resolve().parents[1]
TENK = ROOT / "data/vnext_10k"
DERIVED = TENK / "reverse_projection"
MANIFEST = TENK / "reverse_projection_manifest.json"
SPLITS = ("train", "dev", "test")


def rows(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        yield from (json.loads(line) for line in stream if line.strip())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_arm(arm: str) -> dict[str, dict]:
    return {
        row["record_id"]: row
        for split in SPLITS
        for row in rows(TENK / "views" / arm / f"{split}.jsonl.gz")
    }


def test_reverse_projection_manifest_hashes_and_authority():
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["schema_version"] == "hmltn-reverse-projection-manifest-1.0.0"
    assert manifest["view_family"] == "HML_IN_JSON_OUT"
    assert manifest["authority"] == {
        **manifest["authority"],
        "canonical_data_commit": "09521ae992af5ca583a346da66c93d986e709386",
        "contract_version": "vnext-translation-contract-1.0.0",
        "fable_result_commit": "ccf2a43",
        "hml_semantic_commit": "68178f07784d2a17a9aed9c4dedbea9c740c97a0",
        "source_export_commit": "a2f992a6d474638814a1f1f7809f4015db3894c5",
    }
    assert manifest["derivation"] == {
        "input": "byte-identical HML_LINEAR.input_text joined by record_id",
        "kind": "DETERMINISTIC_RECORD_ID_JOIN",
        "semantic_translation": False,
        "target": "byte-identical AST.target_text joined by record_id",
    }
    for relative, expected in manifest["files"].items():
        path = TENK / relative
        assert path.stat().st_size == expected["bytes"]
        assert sha(path) == expected["sha256"]
    for relative, expected in manifest["source_files"].items():
        path = TENK / relative
        assert path.stat().st_size == expected["bytes"]
        assert sha(path) == expected["sha256"]


def test_reverse_projection_is_a_pure_execute_record_join():
    canonical = {
        row["record_id"]: row
        for split in SPLITS
        for row in rows(TENK / f"{split}.jsonl.gz")
        if row["task_eligibility"]["EXECUTE"]
    }
    hml = load_arm("HML_LINEAR")
    ast = load_arm("AST")
    joined = load_arm("HML_IN_JSON_OUT")
    assert len(hml) == len(ast) == 10000
    assert len(joined) == len(canonical) == 4024
    assert set(joined) == set(canonical)
    split_counts = Counter()
    action_counts = Counter()
    for record_id, item in joined.items():
        hml_item = hml[record_id]
        ast_item = ast[record_id]
        canonical_item = canonical[record_id]
        assert set(item) == {
            "audit_metadata",
            "input_text",
            "record_id",
            "representation",
            "split",
            "target_text",
            "task_eligibility",
        }
        assert item["representation"] == "HML_IN_JSON_OUT"
        assert item["input_text"] == hml_item["input_text"]
        assert item["target_text"] == ast_item["target_text"]
        assert item["split"] == hml_item["split"] == ast_item["split"] == canonical_item["split"]
        assert item["task_eligibility"] == hml_item["task_eligibility"] == ast_item["task_eligibility"]
        assert item["audit_metadata"]["canonical_transition_sha256"] == canonical_item["canonical_sha256"]
        assert item["audit_metadata"]["action_provenance"] == hml_item["audit_metadata"]["action_provenance"]
        assert item["audit_metadata"]["action_provenance"] == ast_item["audit_metadata"]["action_provenance"]
        assert item["audit_metadata"]["input_sha256"] == hml_item["audit_metadata"]["input_sha256"]
        assert item["audit_metadata"]["target_sha256"] == ast_item["audit_metadata"]["target_sha256"]
        hml_action = action_from_hml(item["input_text"])
        assert hml_action == action_from_ast(ast_item["input_text"])
        present = [field for field in ("tactic_text", "action_text") if hml_action.get(field)]
        assert len(present) == 1
        action_counts[present[0]] += 1
        split_counts[item["split"]] += 1
    assert split_counts == {"train": 3254, "dev": 392, "test": 378}
    assert action_counts == {"tactic_text": 4000, "action_text": 24}


def test_reverse_projection_membership_leakage_and_mechanisms():
    raw = json.loads((DERIVED / "raw_execute_membership.json").read_text())
    assert raw["counts"] == {"train": 3254, "dev": 392, "test": 378}
    all_ids = [record_id for split in SPLITS for record_id in raw["record_ids_by_split"][split]]
    assert len(all_ids) == len(set(all_ids)) == 4024

    fresh = list(rows(DERIVED / "leakage_audit.jsonl.gz"))
    original = {
        row["record_id"]: row for row in rows(TENK / "action_leakage_audit.jsonl.gz")
    }
    assert len(fresh) == 4024
    for item in fresh:
        assert item["view_family"] == "HML_IN_JSON_OUT"
        assert item["classification"] == "A_LEGITIMATE_ACTION_SEMANTICS"
        assert item["excluded_from_execute"] is False
        policy_fields = {
            key: value
            for key, value in item.items()
            if key not in {"input_sha256", "target_sha256", "view_family"}
        }
        assert policy_fields == original[item["record_id"]]

    manifest = json.loads(MANIFEST.read_text())
    assert manifest["leakage"] == {
        "ambiguous": 0,
        "checked": 4024,
        "direct_target_revealing": 0,
        "path": "reverse_projection/leakage_audit.jsonl.gz",
        "result": "PASS",
    }
    assert manifest["mechanism_counts"] == {
        "assumption": 24,
        "branch_join": 8,
        "goal_close": 1659,
        "goal_create": 292,
        "implicit_logical_weakening": 16,
        "nested_branch": 24,
        "obligations": 8,
        "ordinary_claim_derivation": 4000,
    }


def test_reverse_projection_fit_population_is_control_safe():
    fit = json.loads((DERIVED / "matched_fit_ids_maxseq6144.json").read_text())
    expected = {
        "train": {"raw": 3254, "hml_in_json_out_fit": 3247, "ast_control_fit": 3239,
                  "pair_fit": 3238, "completed_four_arm_control_fit": 3233,
                  "comparison_fit": 3233},
        "dev": {"raw": 392, "hml_in_json_out_fit": 392, "ast_control_fit": 391,
                "pair_fit": 391, "completed_four_arm_control_fit": 391,
                "comparison_fit": 391},
        "test": {"raw": 378, "hml_in_json_out_fit": 378, "ast_control_fit": 377,
                 "pair_fit": 377, "completed_four_arm_control_fit": 377,
                 "comparison_fit": 377},
    }
    for split, counts in expected.items():
        assert {key: fit["by_split"][split][key] for key in counts} == counts
        for arm in ("hml_in_json_out", "ast_control"):
            for exclusion in fit["by_split"][split][f"{arm}_exclusions"]:
                assert exclusion["fits"] is False
                assert exclusion["fit_length"] > 6144
                assert exclusion["fit_length"] == exclusion["total"] + 16
    assert fit["by_split"]["train"]["excluded_by_hml_in_json_out_only"] == [
        "VN10K-LEAN-2396"
    ]
    assert fit["by_split"]["dev"]["excluded_by_hml_in_json_out_only"] == []
    assert fit["by_split"]["test"]["excluded_by_hml_in_json_out_only"] == []
    assert fit["equivalence_checks"] == {
        "completed_four_arm_control_fit_is_subset_of_hml_in_json_out_fit": True,
        "pair_fit_equals_completed_four_arm_control_fit": False,
        "pair_fit_equals_reusable_comparison_fit": False,
        "reusable_comparison_fit_equals_completed_four_arm_control_fit": True,
    }
    selected = fit["comparison_record_ids_by_split"]
    assert {split: len(selected[split]) for split in SPLITS} == {
        "train": 3233, "dev": 391, "test": 377,
    }
    assert len(set().union(*(set(selected[split]) for split in SPLITS))) == 4001


def test_reverse_projection_token_contract_and_goldens():
    audit = json.loads((DERIVED / "token_audit.json").read_text())
    assert audit["counting_contract"]["maxseq"] == 6144
    assert audit["counting_contract"]["generation_reserve"] == 16
    assert audit["tokenizer"]["model_revision"] == "0f35c6f6d386f7f74e628bd7c6526ce531212300"
    joined = audit["arms"]["HML_IN_JSON_OUT"]["all"]
    control = audit["arms"]["AST_JSON_IN_JSON_OUT_CONTROL"]["all"]
    assert joined["fit"] == 4017
    assert joined["input"]["mean"] == 446.476
    assert joined["target"]["mean"] == 671.881
    assert joined["total"]["mean"] == 1118.357
    assert control["fit"] == 4007
    assert control["input"]["mean"] == 595.611
    assert control["target"]["mean"] == 671.881
    assert control["total"]["mean"] == 1267.493

    goldens = json.loads((DERIVED / "golden_checks.json").read_text())["checks"]
    assert [item["category"] for item in goldens] == [
        "ordinary_derivation", "goal_close", "goal_create", "assumption_nested_branch",
    ]
    assert all(item["input_identity"] and item["target_identity"] for item in goldens)
