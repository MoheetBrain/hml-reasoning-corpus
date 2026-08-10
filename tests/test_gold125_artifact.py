#!/usr/bin/env python3
"""Read-only regression checks for the Gold-125 semantic-discovery artifact."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HML = ROOT / "hml_core"
MANIFEST = ROOT / "manifests/gold125_math_v1.json"
TRAJECTORIES = ROOT / "data/gold125/trajectories"
REPORTS = ROOT / "reports"


class Gold125ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.records = cls.manifest["records"]
        cls.new_records = [record for record in cls.records if not record["frozen_gold25"]]
        cls.new_trajectories = [
            json.loads((TRAJECTORIES / f"{record['problem_id']}.json").read_text(encoding="utf-8"))
            for record in cls.new_records
        ]

    def test_exact_stop_count_and_selection_quotas(self) -> None:
        self.assertEqual(len(self.records), 125)
        self.assertEqual(len(self.new_records), 100)
        self.assertEqual(
            {record["problem_id"] for record in self.new_records},
            {f"MATH-GOLD-{index:03d}" for index in range(26, 126)},
        )
        self.assertEqual(Counter(record["category"] for record in self.new_records), Counter({
            "Algebra": 15,
            "Intermediate Algebra": 15,
            "Counting & Probability": 15,
            "Number Theory": 15,
            "Precalculus": 15,
            "Geometry": 12,
            "Prealgebra": 13,
        }))
        self.assertFalse((TRAJECTORIES / "MATH-GOLD-126.json").exists())

    def test_source_fidelity_and_trajectory_invariants(self) -> None:
        for trajectory in self.new_trajectories:
            self.assertEqual(
                hashlib.sha256(
                    (trajectory["problem"] + "\n" + trajectory["original_solution"]).encode("utf-8")
                ).hexdigest(),
                trajectory["source_hash"],
            )
            self.assertTrue(trajectory["source_quality"]["source_spans_exact"])
            previous_state = trajectory["initial_state"]
            previous_id = "S0"
            available = {fact["id"] for fact in previous_state["facts"]}
            for step in trajectory["steps"]:
                self.assertIn(step["atomicity"], {"ATOMIC", "COMPOUND_MACRO", "UNCERTAIN"})
                self.assertEqual(step["result"]["statement"], step["source_span"])
                self.assertIn(step["source_span"], trajectory["original_solution"])
                self.assertEqual(step["state_before"]["id"], previous_id)
                self.assertEqual(step["state_after"]["id"], f"S{step['step_id'][1:]}")
                self.assertTrue(set(step["dependencies"]) <= available)
                before_ids = {fact["id"] for fact in step["state_before"]["facts"]}
                after_ids = {fact["id"] for fact in step["state_after"]["facts"]}
                self.assertEqual(after_ids - before_ids, {step["result"]["id"]})
                self.assertEqual(before_ids - after_ids, set())
                self.assertEqual(step["state_change"]["added_facts"], [step["result"]["id"]])
                previous_state = step["state_after"]
                previous_id = previous_state["id"]
                available.add(step["result"]["id"])

    def test_artifact_and_audit_reports_exist(self) -> None:
        required = [
            REPORTS / "gold125_selection_audit.md",
            REPORTS / "gold125_semantic_audit.md",
            REPORTS / "gold125_reasoning_synthesis.md",
            REPORTS / "gold125_state_profile.md",
            REPORTS / "thinking_vs_execution_gold125.md",
            REPORTS / "operation_long_tail_analysis_gold125.md",
            REPORTS / "gold125_hml_coverage.md",
            REPORTS / "gold125_gap_analysis.md",
            REPORTS / "gold125_saturation.json",
            REPORTS / "gold125_topk_coverage.json",
            REPORTS / "gold125_independent_audits.json",
            REPORTS / "gold125_audit_machine_results.json",
            REPORTS / "gold125_branch_scope_audit.json",
        ]
        for path in required:
            self.assertTrue(path.exists(), path)
        audits = json.loads((REPORTS / "gold125_audit_machine_results.json").read_text())
        self.assertEqual(len(audits), 100)
        self.assertTrue(all(record["status"] == "PASS" for record in audits))
        hard = json.loads((REPORTS / "gold125_independent_audits.json").read_text())
        self.assertGreaterEqual(len(hard), 15)
        self.assertTrue(all(record["verdict"] == "PASS" for record in hard))
        synthesis = (REPORTS / "gold125_reasoning_synthesis.md").read_text(encoding="utf-8")
        self.assertIn("Gold-125 is complete.", synthesis)
        self.assertIn("Problem 126 was not processed.", synthesis)
        saturation = json.loads((REPORTS / "gold125_saturation.json").read_text())
        self.assertTrue(all("new_semantic_gap_classes" in row for row in saturation))

    def test_hml_pin_clean_and_read_only(self) -> None:
        expected = self.manifest["hml_core_head"]
        actual = subprocess.check_output(["git", "-C", str(HML), "rev-parse", "HEAD"], text=True).strip()
        self.assertEqual(actual, expected)
        self.assertEqual(subprocess.check_output(["git", "-C", str(HML), "status", "--porcelain"], text=True), "")
        writable = []
        for directory, dirnames, filenames in os.walk(HML):
            for name in dirnames + filenames:
                path = Path(directory) / name
                if path.is_symlink():
                    continue
                if os.stat(path).st_mode & 0o222:
                    writable.append(str(path))
        self.assertEqual(writable, [])


if __name__ == "__main__":
    unittest.main()
