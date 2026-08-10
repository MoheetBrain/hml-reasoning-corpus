#!/usr/bin/env python3
"""Regression and acceptance tests for the experimental semantic firewall."""

from __future__ import annotations

import hashlib
import inspect
import json
import subprocess
import unittest
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from experiments.semantic_firewall import reference_checker
from experiments.semantic_firewall.reference_checker import check_case


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "experiments/semantic_firewall"
HML = ROOT / "hml_core"
GOLD125 = ROOT / "manifests/gold125_math_v1.json"
EXPECTED_HML = "5688aba18632b65a8709aa1d85577d31a67dba6a"


def load_cases(split: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    base = HERE / "data" / split.lower()
    cases = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((base / "cases").glob("*.json"))]
    labels = json.loads((base / "labels.json").read_text(encoding="utf-8"))
    return cases, labels


def canonical_sha(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def diff_paths(left: Any, right: Any, prefix: str = "") -> list[str]:
    if type(left) is not type(right):
        return [prefix]
    if isinstance(left, dict):
        out = []
        for key in sorted(set(left) | set(right)):
            path = f"{prefix}.{key}" if prefix else key
            if key not in left or key not in right:
                out.append(path)
            else:
                out.extend(diff_paths(left[key], right[key], path))
        return out
    if isinstance(left, list):
        if len(left) != len(right):
            return [prefix]
        out = []
        for index, (a, b) in enumerate(zip(left, right)):
            out.extend(diff_paths(a, b, f"{prefix}[{index}]"))
        return out
    return [] if left == right else [prefix]


class SemanticFirewallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dev_cases, cls.dev_labels = load_cases("DEV")
        cls.final_cases, cls.final_labels = load_cases("FINAL")
        cls.fixtures = json.loads((HERE / "acceptance/fixtures.json").read_text(encoding="utf-8"))["fixtures"]

    def test_exact_benchmark_counts_and_balance(self) -> None:
        self.assertEqual(len(self.dev_cases), 40)
        self.assertEqual(len(self.final_cases), 160)
        labels = {**self.dev_labels, **self.final_labels}
        self.assertEqual(Counter(item["expected"] for item in labels.values()), Counter({"VALID": 100, "INVALID": 100}))
        self.assertEqual(len({case["pair_id"] for case in self.dev_cases + self.final_cases}), 100)
        for split_labels, expected_per_class in ((self.dev_labels, 2), (self.final_labels, 8)):
            invalid = [item["error_class"] for item in split_labels.values() if item["expected"] == "INVALID"]
            self.assertEqual(set(invalid), set(reference_checker.ERROR_CLASS_FOR.values()))
            self.assertTrue(all(count == expected_per_class for count in Counter(invalid).values()))

    def test_final_is_held_out_from_gold125(self) -> None:
        gold = json.loads(GOLD125.read_text(encoding="utf-8"))["records"]
        gold_rows = {record["source_row_id"] for record in gold}
        gold_hashes = {record["source_hash"] for record in gold}
        self.assertTrue(all(not case["source"]["gold125_overlap"] for case in self.final_cases))
        self.assertFalse({case["source"]["source_row_id"] for case in self.final_cases} & gold_rows)
        self.assertFalse({case["source"]["source_hash"] for case in self.final_cases} & gold_hashes)
        self.assertEqual({case["source"]["level"] for case in self.final_cases}, {"Level 4", "Level 5"})
        self.assertEqual(
            Counter(case["source"]["category"] for case in self.final_cases),
            Counter({"Intermediate Algebra": 68, "Number Theory": 52, "Counting & Probability": 40}),
        )

    def test_source_spans_are_content_addressed(self) -> None:
        for case in self.dev_cases + self.final_cases:
            source = case["source"]
            self.assertEqual(hashlib.sha256(source["solution_span"].encode("utf-8")).hexdigest(), source["solution_span_hash"])
            self.assertTrue(source["problem"].strip())
            self.assertTrue(source["solution_span"].strip())

    def test_checker_matches_every_frozen_label_and_class(self) -> None:
        for cases, labels in ((self.dev_cases, self.dev_labels), (self.final_cases, self.final_labels)):
            for case in cases:
                result = check_case(case)
                label = labels[case["case_id"]]
                self.assertEqual(result["verdict"], label["expected"], case["case_id"])
                if label["expected"] == "INVALID":
                    self.assertEqual(result["error_class"], label["error_class"], case["case_id"])
                    self.assertTrue(result["supporting_evidence"])

    def test_checker_has_no_label_channel(self) -> None:
        source = inspect.getsource(reference_checker)
        self.assertNotIn("labels.json", source)
        self.assertNotIn("freeze_manifest", source)
        for case in self.dev_cases + self.final_cases:
            self.assertNotIn("expected", case)
            self.assertNotIn("error_class", case)
            self.assertNotIn("corruption", case)

    def test_matched_twins_have_only_declared_minimal_corruption(self) -> None:
        all_cases = self.dev_cases + self.final_cases
        all_labels = {**self.dev_labels, **self.final_labels}
        by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for case in all_cases:
            by_pair[case["pair_id"]].append(case)
        for pair_id, twins in by_pair.items():
            self.assertEqual(len(twins), 2)
            valid = next(case for case in twins if all_labels[case["case_id"]]["expected"] == "VALID")
            invalid = next(case for case in twins if all_labels[case["case_id"]]["expected"] == "INVALID")
            valid_cmp = json.loads(json.dumps(valid))
            invalid_cmp = json.loads(json.dumps(invalid))
            valid_cmp["case_id"] = invalid_cmp["case_id"] = "PAIR"
            differences = diff_paths(valid_cmp, invalid_cmp)
            targets = all_labels[invalid["case_id"]]["corruption"]["target_paths"]
            self.assertTrue(differences, pair_id)
            for difference in differences:
                self.assertTrue(
                    any(difference.startswith(target) or target.startswith(difference) for target in targets),
                    f"{pair_id}: undeclared difference {difference}; targets={targets}",
                )
            sizes = [len(json.dumps(case, sort_keys=True, ensure_ascii=False)) for case in twins]
            self.assertLessEqual(max(sizes) / min(sizes), 1.06, pair_id)

    def test_acceptance_fixtures_cover_legal_illegal_unknown(self) -> None:
        self.assertEqual(len(self.fixtures), 30)
        self.assertEqual(Counter(item["boundary"] for item in self.fixtures), Counter({"LEGAL": 10, "ILLEGAL": 10, "BOUNDARY_UNKNOWN": 10}))
        self.assertEqual(Counter(item["invariant"] for item in self.fixtures), Counter({name: 3 for name in reference_checker.INVARIANTS}))
        for fixture in self.fixtures:
            result = check_case(fixture["case"])
            self.assertEqual(result["verdict"], fixture["expected_reference_result"], fixture["fixture_id"])
            if result["verdict"] == "INVALID":
                self.assertEqual(result["error_class"], fixture["expected_error_class"])
            self.assertIn(
                fixture["current_hml_support"],
                {"CURRENT_HML_PASS", "CURRENT_HML_PARTIAL", "CURRENT_HML_FAIL", "CURRENT_HML_NOT_EXPRESSIBLE"},
            )

    def test_renderings_derive_from_identical_neutral_record(self) -> None:
        for case in self.dev_cases + self.final_cases:
            split = case["split"].lower()
            rendering = json.loads((HERE / "renderings" / split / f"{case['case_id']}.json").read_text(encoding="utf-8"))
            self.assertEqual(rendering["semantic_sha256"], canonical_sha(case))
            self.assertEqual(rendering["generic_typed_ast"]["fields"], case)
            self.assertEqual(rendering["hml"]["adapter_envelope"], case)
            self.assertFalse(rendering["hml"]["pure_current_hml_equivalent"])
            self.assertIn(case["case_id"], rendering["structured_english"])

    def test_freeze_manifest_hashes_every_protocol_artifact(self) -> None:
        manifest_path = HERE / "freeze_manifest.json"
        expected = (HERE / "freeze_manifest.sha256").read_text(encoding="utf-8").split()[0]
        self.assertEqual(hashlib.sha256(manifest_path.read_bytes()).hexdigest(), expected)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for record in manifest["files"]:
            path = ROOT / record["path"]
            self.assertTrue(path.exists(), path)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["sha256"], path)
        self.assertEqual(manifest["counts"]["final_gold125_overlap"], 0)

    def test_read_only_current_hml_probe_and_pin(self) -> None:
        probe = json.loads((HERE / "results/current_hml_probe.json").read_text(encoding="utf-8"))
        self.assertEqual(probe["hml_core_sha"], EXPECTED_HML)
        self.assertFalse(probe["hml_modified"])
        self.assertEqual(len(probe["probes"]), 13)
        for item in probe["probes"]:
            expectation = item["expectation"]
            if "ok" in expectation:
                self.assertEqual(item["ok"], expectation["ok"], item["probe_id"])
            for key in ("d1", "d2"):
                if key in expectation:
                    self.assertEqual(item["derivation_status"].get(key), expectation[key], item["probe_id"])
            if "g1" in expectation:
                self.assertEqual(item["goal_status"].get("g1"), expectation["g1"], item["probe_id"])
            if "diagnostic" in expectation:
                self.assertIn(expectation["diagnostic"], item["diagnostic_codes"], item["probe_id"])
        actual = subprocess.check_output(["git", "-C", str(HML), "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "-C", str(HML), "status", "--porcelain", "--untracked-files=all"], text=True)
        self.assertEqual(actual, EXPECTED_HML)
        self.assertEqual(dirty, "")


if __name__ == "__main__":
    unittest.main()
