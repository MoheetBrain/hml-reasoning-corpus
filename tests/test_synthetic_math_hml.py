import json
import hashlib
import re
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "MASTER_SYNTHETIC_MATH_HML.md"
BRANCH_ARTIFACT = ROOT / "data/synthetic_math_branch_ancestry_v1.json"
BRANCH_SCHEMA = ROOT / "schemas/synthetic-math-branch-ancestry.schema.json"
INITIAL_ARTIFACT = ROOT / "data/synthetic_math_initial_premises_v1.json"
INITIAL_SCHEMA = ROOT / "schemas/synthetic-math-initial-premises.schema.json"
IMPLICIT_ARTIFACT = ROOT / "data/synthetic_math_implicit_logical_steps_v1.json"
IMPLICIT_SCHEMA = ROOT / "schemas/synthetic-math-implicit-logical-steps.schema.json"
CORRECTION_ARTIFACT = ROOT / "data/synthetic_math_canonicalization_corrections_v1.json"
CORRECTION_SCHEMA = ROOT / "schemas/synthetic-math-canonicalization-corrections.schema.json"
OBLIGATION_CORRECTION = ROOT / "data/fx_obl_unknown_expectation_correction_vnext.json"


def _text() -> str:
    return MASTER.read_text(encoding="utf-8")


def test_exactly_six_complete_hundred_problem_corpora():
    text = _text()
    found = re.findall(r"(?m)^## (ALG|GEN|CALC|PROB|LINALG|MIXED)-(\d{3}) —", text)
    assert len(found) == 600
    for corpus in ("ALG", "GEN", "CALC", "PROB", "LINALG", "MIXED"):
        numbers = sorted(int(number) for key, number in found if key == corpus)
        assert numbers == list(range(1, 101))


def test_transition_count_reconciles_and_every_transition_is_classified():
    text = _text()
    declared = int(re.search(r"\| Atomic reasoning transitions \| (\d+) \|", text).group(1))
    headings = re.findall(r"(?m)^#### (?:ALG|GEN|CALC|PROB|LINALG|MIXED)-\d{3}-T\d{3}$", text)
    classifications = re.findall(r"(?m)^- \*\*Classification:\*\* `[^`]+`", text)
    assert len(headings) == declared
    assert len(classifications) == declared


def test_hml_validation_counts_reconcile_and_no_invalid_is_accepted():
    text = _text()
    rendered = int(re.search(r"\| Frozen-HML renderings emitted \| (\d+) \|", text).group(1))
    schema_pass = int(re.search(r"\| Neutral-schema validations passed \| (\d+) \|", text).group(1))
    roundtrips = int(re.search(r"\| Frozen-HML exact round trips \| (\d+) \|", text).group(1))
    assert text.count("~~~~hml\n") == rendered
    assert text.count("schema `PASS`; HML round trip `PASS`") == schema_pass == roundtrips
    assert "runtime verdict `INVALID`" not in text
    assert "| Frozen-HML `INVALID` verdicts accepted | 0 |" in text


def test_every_problem_preserves_full_source_and_final_result():
    text = _text()
    assert text.count("<details><summary>Open complete source problem and worked solution</summary>") == 600
    assert text.count("### Final mathematical result") == 600
    assert text.count("### Candidate / branch / obligation ledger") == 600


def test_frozen_authority_is_explicit():
    text = _text()
    assert "hml-semantic-pre-gemma-v1" in text
    assert "84bf9897689b0ed78a2caaefc1db850d49b81260" in text
    assert "semantic-firewall-case-0.1.0" in text


def test_branch_ancestry_artifact_is_schema_valid_and_complete():
    artifact = json.loads(BRANCH_ARTIFACT.read_text(encoding="utf-8"))
    schema = json.loads(BRANCH_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(artifact)
    partitions = [partition for problem in artifact["problems"] for partition in problem["partitions"]]
    branches = [branch for partition in partitions for branch in partition["branches"]]
    assert len(artifact["problems"]) == 28
    assert len(partitions) == 30
    assert len(branches) == 66
    assert sum(branch["opening_transition_id"] is not None for branch in branches) == 61
    assert sum(branch["opening_transition_id"] is None for branch in branches) == 5


def test_sibling_branches_share_explicit_parent_and_reject_linear_leakage():
    artifact = json.loads(BRANCH_ARTIFACT.read_text(encoding="utf-8"))
    for problem in artifact["problems"]:
        for partition in problem["partitions"]:
            parent_ids = partition["pre_split_premise_ids"]
            assert parent_ids
            assert {premise["premise_id"] for premise in partition["pre_split_premises"]} == set(parent_ids)
            for branch in partition["branches"]:
                assert branch["pre_split_premise_ids"] == parent_ids
                assert branch["opening_dependency_ids"] == parent_ids
            for previous, sibling in zip(partition["branches"], partition["branches"][1:]):
                if previous["transition_ids"] and sibling["opening_transition_id"]:
                    previous_terminal = "c" + previous["transition_ids"][-1].rsplit("T", 1)[1]
                    assert previous_terminal not in sibling["opening_dependency_ids"]


def test_segmenter_omitted_parent_premises_are_exact_source_backed_states():
    artifact = json.loads(BRANCH_ARTIFACT.read_text(encoding="utf-8"))
    omitted = []
    for problem in artifact["problems"]:
        for partition in problem["partitions"]:
            for premise in partition["pre_split_premises"]:
                if premise["origin"] == "EXPLICIT_SOURCE_STATE_OMITTED_BY_OLD_SEGMENTER":
                    omitted.append((problem["problem_id"], premise["premise_id"], premise["proposition"]))
    assert omitted == [
        ("GEN-056", "sp001", "u=2^x."),
        ("GEN-100", "sp001", r"\left| \frac{x-1}{x+2} \right| =2."),
    ]


def test_initial_premises_are_explicit_for_all_600_problems_and_source_hashed():
    artifact = json.loads(INITIAL_ARTIFACT.read_text(encoding="utf-8"))
    schema = json.loads(INITIAL_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(artifact)
    assert len(artifact["problems"]) == 600
    assert len({problem["problem_id"] for problem in artifact["problems"]}) == 600
    premises = [premise for problem in artifact["problems"] for premise in problem["premises"]]
    assert len(premises) == 1248
    assert sum(item["source_origin"] == "SOURCE_INITIAL_STATE" for item in premises) == 648
    for problem in artifact["problems"]:
        assert problem["premises"][0]["premise_id"] == "p0"
        assert [item["premise_id"] for item in problem["premises"][1:]] == [
            f"i{index:03d}" for index in range(1, len(problem["premises"]))
        ]
        for premise in problem["premises"]:
            assert hashlib.sha256(premise["source_span"].encode()).hexdigest() == premise["source_span_sha256"]
            assert premise["source_problem_sha256"] == problem["source_problem_sha256"]
            assert premise["dependencies"] == []


def test_mixed_039_has_one_source_backed_canonical_role():
    artifact = json.loads(CORRECTION_ARTIFACT.read_text(encoding="utf-8"))
    schema = json.loads(CORRECTION_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(artifact)
    corrections = {item["transition_id"]: item for item in artifact["corrections"]}
    assert set(corrections) == {
        "MIXED-039-T008", "GEN-087-T013", "GEN-087-T016", "GEN-094-T002", "GEN-094-T003"
    }
    correction = corrections["MIXED-039-T008"]
    assert correction["transition_id"] == "MIXED-039-T008"
    assert correction["old_role"]["gap_code"] == "CANDIDATE_CREATION_NOT_REPRESENTABLE"
    assert correction["corrected_role"]["semantic_object"] == "DERIVED_DISJUNCTIVE_CLAIM"
    assert correction["corrected_role"]["gap_code"] is None
    assert len(correction["affected_downstream_ids"]) == 6
    text = _text()
    block = text.split("#### MIXED-039-T008", 1)[1].split("#### MIXED-039-T009", 1)[0]
    assert "CANDIDATE_CREATION_NOT_REPRESENTABLE" not in block
    assert "`REPRESENTABLE_BUT_CURRENTLY_UNVERIFIABLE`" in block


def test_only_d063_implicit_or_introductions_are_inserted():
    artifact = json.loads(IMPLICIT_ARTIFACT.read_text(encoding="utf-8"))
    schema = json.loads(IMPLICIT_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(artifact)
    assert len(artifact["steps"]) == 16
    assert {step["source_join_transition_id"] for step in artifact["steps"]} == {
        "ALG-097-T014", "ALG-099-T015", "GEN-054-T018", "GEN-062-T013",
        "GEN-072-T009", "MIXED-039-T014"
    }
    for step in artifact["steps"]:
        assert step["record_kind"] == "IMPLICIT_LOGICAL_STEP"
        assert step["warrant_rule"] == "DISJUNCTION_INTRODUCTION"
        assert step["deterministic_derivation_proof"]["premise_equals_selected_disjunct"] is True
        assert len(step["premise_ids"]) == 1


def test_fx_obl_unknown_expectation_is_corrected_without_mutating_history():
    correction = json.loads(OBLIGATION_CORRECTION.read_text(encoding="utf-8"))
    fixture_path = ROOT / correction["historical_fixture_file"]
    assert hashlib.sha256(fixture_path.read_bytes()).hexdigest() == correction["historical_fixture_file_sha256"]
    fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))["fixtures"]
    fixture = next(item for item in fixtures if item["fixture_id"] == "FX-OBL-UNKNOWN")
    canonical = json.dumps(fixture, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    assert hashlib.sha256(canonical.encode()).hexdigest() == correction["historical_fixture_canonical_sha256"]
    assert fixture["expected_reference_result"] == "UNRESOLVED"
    assert correction["vnext_expectation"] == {
        "verdict": "INVALID",
        "error_class": "OBLIGATION_DROP",
        "structural_cause": "obligations.o_prev was removed from state_after rather than retained and discharged",
    }
    assert correction["historical_fixture_mutated"] is False
    assert correction["hml_structural_checks_weakened"] is False
