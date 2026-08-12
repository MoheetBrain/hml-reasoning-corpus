from __future__ import annotations

import hashlib
import json
import os
import subprocess
import unittest
from collections import defaultdict
from pathlib import Path

from synthetic_factory_v2.audits import contradiction_audit, leakage_audit
from synthetic_factory_v2.authority import verify_authority
from synthetic_factory_v2.canonical import jsonl_bytes, learner_hash, sha256_file
from synthetic_factory_v2.constants import CONTRACTS, SENTINELS
from synthetic_factory_v2.factory_b import generate as generate_b


ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return [json.loads(line) for line in (ROOT / path).read_text().splitlines()]


class AuthorityTests(unittest.TestCase):
    def test_authority_pinned(self):
        result = verify_authority()
        self.assertEqual(result["status"], "AUTHORITY_VERIFIED")

    def test_hml_unmodified_and_read_only(self):
        hml = Path(os.environ["HML_FROZEN_PATH"])
        self.assertEqual(subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=hml, text=True, capture_output=True, check=True).stdout, "")
        self.assertFalse(any(path.stat().st_mode & 0o222 for path in hml.rglob("*") if path.is_file()))


class FactoryBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load("data/factory_b/gold_stage100.jsonl")

    def test_representation_neutral_source(self):
        self.assertEqual(len(self.rows), 100)
        for row in self.rows:
            self.assertEqual(row["renderings"], {})

    def test_prediction_contract_type_and_hash(self):
        for row in self.rows:
            self.assertEqual(row["prediction_contract"], "ACTION_APPLICABILITY")
            self.assertIn(row["prediction_contract"], CONTRACTS)
            self.assertEqual(row["learner_input_hash"], learner_hash(row["prediction_contract"], row["oracle"]["transition"]))

    def test_no_contradictory_inputs_or_duplicates(self):
        self.assertEqual(contradiction_audit(self.rows)["conflicting_input_count"], 0)
        self.assertEqual(len({row["learner_input_hash"] for row in self.rows}), 100)

    def test_no_theorem_leakage(self):
        self.assertTrue(all(value == 0 for value in leakage_audit(self.rows)["overlap_counts"].values()))

    def test_no_sentinels_in_gold(self):
        for row in self.rows:
            source = json.dumps(row["canonical_source"]).lower()
            self.assertFalse(any(token in source for token in SENTINELS))

    def test_no_secondary_findings(self):
        for row in self.rows:
            self.assertEqual(row["secondary_findings"], 0)

    def test_unknown_is_not_collapsed_to_negative(self):
        for row in self.rows:
            verdict = row["oracle"]["result"]["verdict"]
            self.assertEqual(row["label"], "APPLICABLE" if verdict == "VALID" else "NOT_APPLICABLE")
            self.assertNotEqual(verdict, "UNRESOLVED")

    def test_positive_alternatives_exist(self):
        groups = defaultdict(list)
        for row in self.rows:
            groups[row["neighborhood_id"]].append(row)
        alternatives = sum(max(0, sum(row["label"] == "APPLICABLE" for row in group) - 1) for group in groups.values())
        self.assertGreater(alternatives, 0)

    def test_deterministic_generation(self):
        first = generate_b()
        second = generate_b()
        self.assertEqual(hashlib.sha256(jsonl_bytes(first)).hexdigest(), hashlib.sha256(jsonl_bytes(second)).hexdigest())


class FactoryATests(unittest.TestCase):
    def test_contracts_are_explicit_and_a2_is_clean(self):
        a1 = load("data/factory_a/a1_regression.jsonl")
        a2 = load("data/factory_a/a2_learning.jsonl")
        self.assertEqual(len(a1), 200)
        self.assertEqual(len(a2), 40)
        self.assertTrue(all(row["prediction_contract"] in CONTRACTS for row in a1 + a2))
        self.assertTrue(all(row["prediction_contract"] == "EVIDENCE_SUFFICIENCY" for row in a2))
        self.assertTrue(all(not row["shortcut_flags"]["contains_sentinel"] and row["secondary_findings"] == 0 for row in a2))


class QualificationTests(unittest.TestCase):
    def test_field_recovery_provenance_and_census(self):
        census = json.loads((ROOT / "manifests/lean_qualification_census.json").read_text())
        self.assertEqual(census["records_scanned"], 241265)
        self.assertEqual(census["eligible"]["EVIDENCE_SUFFICIENCY"], 0)
        self.assertEqual(census["theorem_split_overlap_count"], 0)
        self.assertEqual(census["split_record_counts"], {"TRAIN": 192882, "DEV": 24067, "FINAL": 24316})
        self.assertNotIn("LLM_GUESS", set(census["field_provenance"].values()))
        self.assertNotIn("HEURISTIC_GUESS", set(census["field_provenance"].values()))
        self.assertTrue(all(origin in {"DIRECT_SOURCE", "DETERMINISTIC_DERIVATION", "FROZEN_HML_DERIVATION", "FORMAL_BACKEND", "NOT_RECOVERABLE"} for origin in census["field_provenance"].values()))

    def test_dataset_hash_manifest(self):
        manifest = json.loads((ROOT / "manifests/v2_manifest.json").read_text())
        repo = ROOT.parent
        for item in manifest["datasets"].values():
            self.assertEqual(sha256_file(repo / item["path"]), item["sha256"])


if __name__ == "__main__":
    unittest.main()
