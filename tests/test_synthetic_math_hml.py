import json
import re
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "MASTER_SYNTHETIC_MATH_HML.md"
BRANCH_ARTIFACT = ROOT / "data/synthetic_math_branch_ancestry_v1.json"
BRANCH_SCHEMA = ROOT / "schemas/synthetic-math-branch-ancestry.schema.json"


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
    assert len(artifact["problems"]) == 29
    assert len(partitions) == 31
    assert len(branches) == 68
    assert sum(branch["opening_transition_id"] is not None for branch in branches) == 63
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
