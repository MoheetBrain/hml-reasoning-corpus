"""Diagnostic integrity checks for the Gold-25 discovery artifacts.

These tests are read-only: they validate the copied source, neutral trajectories,
manifest fidelity, and the frozen HML submodule without importing or rewriting HML.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/math/train-00000-of-00001-7320a6f3aba8ebd2.parquet"
PROVENANCE = ROOT / "data/raw/math/math_dataset_provenance.json"
MANIFEST = ROOT / "manifests/gold25_math_v0.json"
TRAJECTORIES = ROOT / "data/gold25/trajectories"
HML_CORE = ROOT / "hml_core"
AUDIT_REPORT = ROOT / "reports/gold25_semantic_adversarial_audit.md"
GENERATOR = ROOT / "scripts/build_gold25.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class Gold25DiscoveryIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_dataset_copy_is_byte_identical_to_recorded_source(self) -> None:
        self.assertTrue(RAW.exists())
        self.assertTrue(self.provenance["byte_identical"])
        self.assertEqual(RAW.stat().st_size, self.provenance["bytes"]["destination"])
        self.assertEqual(sha256(RAW), self.provenance["sha256"]["destination"])
        self.assertEqual(self.provenance["sha256"]["original"], self.provenance["sha256"]["destination"])

    def test_manifest_has_exact_gold25_category_targets(self) -> None:
        records = self.manifest["records"]
        self.assertEqual(len(records), 25)
        counts = {}
        for record in records:
            counts[record["category"]] = counts.get(record["category"], 0) + 1
        self.assertEqual(
            counts,
            {
                "Algebra": 5,
                "Intermediate Algebra": 4,
                "Counting & Probability": 4,
                "Number Theory": 4,
                "Precalculus": 3,
                "Geometry": 3,
                "Prealgebra": 2,
            },
        )
        self.assertEqual(len({record["problem_id"] for record in records}), 25)

    def test_trajectories_preserve_source_and_state_chain(self) -> None:
        manifest_by_id = {record["problem_id"]: record for record in self.manifest["records"]}
        paths = sorted(TRAJECTORIES.glob("MATH-GOLD-*.json"))
        self.assertEqual(len(paths), 25)
        for path in paths:
            trajectory = json.loads(path.read_text(encoding="utf-8"))
            record = manifest_by_id[trajectory["problem_id"]]
            self.assertEqual(trajectory["problem"], record["problem"])
            self.assertEqual(trajectory["original_solution"], record["original_solution"])
            self.assertEqual(trajectory["initial_state"]["id"], "S0")
            current = "S0"
            for index, step in enumerate(trajectory["steps"], 1):
                self.assertIn(step["source_span"], trajectory["original_solution"])
                self.assertEqual(step["state_before"]["id"], current)
                self.assertEqual(step["state_after"]["id"], f"S{index}")
                self.assertEqual(step["state_change"]["from"], current)
                self.assertEqual(step["state_change"]["to"], f"S{index}")
                current = f"S{index}"
            self.assertEqual(trajectory["final_state"]["id"], current)
            self.assertEqual(trajectory["goal_status"], "discharged")

    def test_gold25_is_neutral_and_has_no_hml_renderings(self) -> None:
        renderings = [
            path
            for path in (ROOT / "data/gold25").rglob("*")
            if path.is_file() and path.suffix.lower() in {".hml", ".hmlang"}
        ]
        self.assertEqual(renderings, [])
        for path in TRAJECTORIES.glob("*.json"):
            self.assertNotIn("hml_program", json.loads(path.read_text(encoding="utf-8")))

    def test_transition_semantics_have_resolvable_dependencies_and_exact_deltas(self) -> None:
        for path in sorted(TRAJECTORIES.glob("MATH-GOLD-*.json")):
            trajectory = json.loads(path.read_text(encoding="utf-8"))
            available = {fact["id"] for fact in trajectory["initial_state"]["facts"]}
            for step in trajectory["steps"]:
                self.assertTrue(set(step["dependencies"]) <= available, (path.name, step["step_id"]))
                before_facts = {fact["id"] for fact in step["state_before"]["facts"]}
                after_facts = {fact["id"] for fact in step["state_after"]["facts"]}
                self.assertEqual(after_facts - before_facts, {step["result_id"]}, (path.name, step["step_id"]))
                self.assertEqual(before_facts - after_facts, set(), (path.name, step["step_id"]))
                self.assertEqual(step["state_change"]["added_facts"], [step["result_id"]])
                self.assertEqual(
                    step["state_change"]["added_obligations"],
                    [item["id"] for item in step["creates_obligations"]],
                )
                self.assertEqual(step["state_change"]["removed_obligations"], step["discharges_obligations"])
                self.assertEqual(step["state_change"]["from"], step["state_before"]["id"])
                self.assertEqual(step["state_change"]["to"], step["state_after"]["id"])
                if step["action"]["operation_id"] == "DISCHARGE_GOAL":
                    self.assertTrue(all(goal["status"] == "goal_discharged" for goal in step["state_after"]["goals"]))
                available.add(step["result_id"])

    def test_adversarial_audit_report_and_generator_scope(self) -> None:
        self.assertTrue(AUDIT_REPORT.exists())
        audit = AUDIT_REPORT.read_text(encoding="utf-8")
        self.assertIn("all 25 selected problems and all 118 canonical transitions", audit)
        self.assertIn("Independent hard-trajectory audits", audit)
        self.assertIn("MATH-GOLD-006", audit)
        generator = GENERATOR.read_text(encoding="utf-8")
        self.assertIn("Gold-25 curated artifact generator", generator)
        self.assertIn("not a reusable automatic extractor", generator)

    def test_frozen_hml_pin_cleanliness_and_permissions(self) -> None:
        metadata = json.loads((ROOT / "schemas/project_metadata.json").read_text(encoding="utf-8"))
        head = subprocess.check_output(["git", "-C", str(HML_CORE), "rev-parse", "HEAD"], text=True).strip()
        status = subprocess.check_output(["git", "-C", str(HML_CORE), "status", "--porcelain"], text=True)
        writable = subprocess.check_output(["find", str(HML_CORE), "-perm", "+022", "-print"], text=True)
        self.assertEqual(head, metadata["hml_commit_sha"])
        self.assertEqual(status, "")
        self.assertEqual(writable, "")


if __name__ == "__main__":
    unittest.main()
