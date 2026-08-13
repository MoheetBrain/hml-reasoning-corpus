import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "MASTER_SYNTHETIC_MATH_HML.md"
PILOT = ROOT / "experiments/prm800k_audit/results/cross_source_gap_pilot_v1.jsonl"
SUMMARY = ROOT / "experiments/prm800k_audit/results/cross_source_gap_pilot_v1_summary.json"


def test_pool_b_baseline_promotion_and_remaining_histogram_reconcile():
    text = MASTER.read_text(encoding="utf-8")
    assert "`453 verified before → 767 verified after`" in text
    assert text.count("baseline Pool `A`") == 453
    assert text.count("baseline Pool `B`") == 2640
    assert text.count("promoted `B→A`") == 315
    assert text.count("**Remaining verification blocker:**") == 2256
    remaining_pool_b = re.findall(
        r"\*\*Remaining verification blocker:\*\* `([^`]+)`",
        text,
    )
    counts = Counter(remaining_pool_b)
    # Three library classes account for 353 rows, and 10 directly reached missed candidate gaps
    # carry their explicit diagnosis; the rest are the 1,893 rows still in Pool B.
    assert sum(counts.values()) == 2256
    assert sum(counts[name] for name in (
        "THEOREM_OR_DOMAIN_LIBRARY_REQUIREMENT",
        "CALCULUS_RULE_OR_LIBRARY",
        "PROBABILITY_OR_STATISTICS_RULE",
    )) == 353
    assert counts["MISCLASSIFIED_CURRENT_KNOWN_CORE_GAP"] == 10
    assert sum(counts.values()) - 353 - 10 == 1893


def test_every_verified_transition_has_a_hash_bound_external_certificate():
    text = MASTER.read_text(encoding="utf-8")
    blocks = re.split(r"(?m)^#### (?:ALG|GEN|CALC|PROB|LINALG|MIXED)-\d{3}-T\d{3}$", text)[1:]
    verified = [block for block in blocks if "`FULLY_REPRESENTABLE_AND_BACKEND_VERIFIED`" in block]
    assert len(verified) == 767
    assert all("**External check certificate:**" in block for block in verified)

    certificates = re.findall(r"(?m)^- \*\*External check certificate:\*\* `(\{.*\})`$", text)
    # One additionally checked transition remains classified as a library obligation;
    # all 767 verified transitions must still have a certificate.
    assert len(certificates) >= 767
    for raw in certificates:
        certificate = json.loads(raw)
        recorded = certificate.pop("certificate_sha256")
        canonical = json.dumps(certificate, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        assert hashlib.sha256(canonical.encode()).hexdigest() == recorded
        assert certificate["backend"] == "SymPy"
        assert certificate["before_sha256"] and certificate["after_sha256"]


def test_prm_pilot_is_exactly_1000_source_validated_records_and_no_new_core_class():
    rows = [json.loads(line) for line in PILOT.read_text().splitlines()]
    summary = json.loads(SUMMARY.read_text())
    assert len(rows) == len({row["pilot_record_id"] for row in rows}) == 1000
    assert all(row["source_validated_exactly"] for row in rows)
    assert all(row["new_core_semantic_candidate"] is None for row in rows)
    assert Counter(row["hml_judgment"] for row in rows) == Counter(summary["judgment_counts"])
    assert summary["source_validation"] == "1000/1000 exact"
    assert summary["new_core_semantic_candidates"] == 0
    assert summary["marginal_new_semantic_rate"] == 0.0
    assert summary["known_gap_recurrence"] == {
        "branch_create": 25,
        "branch_join": 20,
        "candidate_lifecycle_action_creation": 654,
        "candidate_lifecycle_mathematical_object": 0,
        "exact_approximate_status": 30,
    }


def test_prm_source_labels_are_separate_from_hml_judgments():
    rows = [json.loads(line) for line in PILOT.read_text().splitlines()]
    assert Counter(row["source_process_labels"]["rating"] for row in rows) == Counter({-1: 500, 0: 250, 1: 250})
    assert all("hml_judgment" in row and "source_process_labels" in row for row in rows)
    assert all(
        row["neutral_trajectory"]["warrant"]
        == "PRM800K_SOURCE_LABEL_IS_PROCESS_METADATA_NOT_MATHEMATICAL_AUTHORITY"
        for row in rows
    )
