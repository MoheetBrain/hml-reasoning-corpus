import copy
import json
import unittest
from pathlib import Path

from synthetic_factory.mutations import mutate_valid_case
from synthetic_factory.records import differences
from synthetic_factory.verifier_runner import primary_result


ROOT = Path(__file__).resolve().parents[1]


def records():
    return [json.loads(line) for line in (ROOT / "data/stage100/canonical_pairs.jsonl").read_text().splitlines()]


class MinimalPairTests(unittest.TestCase):
    def test_all_pairs_change_exactly_one_semantic_leaf(self):
        rows = records()
        self.assertEqual(len(rows), 100)
        for row in rows:
            diff = differences(row["source_transition"], row["counterfactual_transition"])
            self.assertEqual(len(diff), 1, row["pair_id"])
            self.assertEqual(diff[0].path, row["exact_changed_field"])

    def test_mutator_does_not_modify_input(self):
        for row in records():
            source = row["source_transition"]
            saved = copy.deepcopy(source)
            mutate_valid_case(source)
            self.assertEqual(source, saved)

    def test_every_pair_replays_with_exact_labels(self):
        for row in records():
            self.assertEqual(primary_result(row["source_transition"])["verdict"], "VALID")
            result = primary_result(row["counterfactual_transition"])
            self.assertEqual(result["verdict"], "INVALID")
            self.assertEqual(result["error_class"], row["failure_code_if_invalid"])


if __name__ == "__main__":
    unittest.main()
