import collections
import json
import unittest
from pathlib import Path

from synthetic_factory.constants import CORPUS_SHA, HML_SHA


ROOT = Path(__file__).resolve().parents[1]


class DatasetContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [json.loads(line) for line in (ROOT / "data/stage100/canonical_pairs.jsonl").read_text().splitlines()]

    def test_balanced_ten_family_stage(self):
        counts = collections.Counter(row["mutation_family"] for row in self.rows)
        self.assertEqual(len(self.rows), 100)
        self.assertEqual(set(counts.values()), {10})
        self.assertEqual(len(counts), 10)

    def test_no_unknown_parser_or_duplicate_negatives(self):
        payloads = {json.dumps(row["counterfactual_transition"], sort_keys=True) for row in self.rows}
        self.assertEqual(len(payloads), 100)
        for row in self.rows:
            self.assertFalse(row["causality"]["parser_or_serialization_artifact"])
            self.assertEqual(row["mutated_verifier_result"]["verdict"], "INVALID")

    def test_forensic_causality_reclassification(self):
        counts = collections.Counter(row["causality"]["classification"] for row in self.rows)
        self.assertEqual(
            counts,
            {"SEMANTIC_HARD_PAIR": 20, "STRUCTURAL_PAIR": 60, "AMBIGUOUS": 20},
        )

    def test_provenance_and_authority_are_complete(self):
        for row in self.rows:
            self.assertEqual(row["hml_sha"], HML_SHA)
            self.assertEqual(row["corpus_sha"], CORPUS_SHA)
            self.assertTrue(row["source_provenance"]["source_file_sha256"])
            self.assertEqual(row["change_count"], 1)


if __name__ == "__main__":
    unittest.main()
