"""Read-only regression checks for ontology-v1 and the bounded AMPS audit."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HML = ROOT / "hml_core"
PIN = "5688aba18632b65a8709aa1d85577d31a67dba6a"
VIEW = ROOT / "data/derived/gold125_ontology_v1/gold125_ontology_v1_all_transitions.json"
DESKTOP_AMPS = Path("/Users/moheet/Desktop/0000.parquet")
REPO_AMPS = ROOT / "data/raw/amps_khan/0000.parquet"


class OntologyV1Tests(unittest.TestCase):
    def test_derived_view_and_quality_gate(self) -> None:
        view = json.loads(VIEW.read_text(encoding="utf-8"))
        self.assertEqual(len(view), 769)
        self.assertEqual({item["trajectory_id"] for item in view}, {f"MATH-GOLD-{i:03d}" for i in range(1, 126)})
        allowed_modes = {"EXECUTION", "SEARCH_META", "VERIFICATION", "MODELING", "GOAL_MANAGEMENT", "OTHER"}
        allowed_layers = {"CORE", "THEOREM_LIBRARY", "DOMAIN_LIBRARY", "SYMBOLIC_BACKEND", "NUMERIC_BACKEND", "SEARCH_META", "UNKNOWN"}
        allowed_uncertainty = {"CERTAIN", "SOURCE_AMBIGUOUS", "ANNOTATION_REVIEW", "UNRESOLVED"}
        for item in view:
            self.assertIn(item["reasoning_mode"], allowed_modes)
            self.assertIn(item["knowledge_layer"], allowed_layers)
            self.assertIn(item["uncertainty"], allowed_uncertainty)
            self.assertIn("provenance", item)
            self.assertIn("observed_operation", item["provenance"])
            self.assertIn("preconditions", item)
            self.assertIn("obligations_created", item)
            self.assertIn("obligations_discharged", item)
            self.assertIn("dependencies", item)
            self.assertIn("state_delta", item)

        gate = json.loads((ROOT / "reports/gold125_ontology_quality_gate.json").read_text(encoding="utf-8"))
        self.assertEqual(gate["before_disagreement_count"], 43)
        self.assertEqual(gate["explained_by_axes_or_uncertainty"], 42)
        self.assertEqual(gate["genuine_semantic_disagreement_count"], 1)
        self.assertEqual(gate["ontology_core_operation_count"], 17)
        self.assertEqual(gate["ontology_core_candidate_operation_count"], 18)
        self.assertEqual(gate["unresolved_transition_count"], 136)
        self.assertEqual(gate["ontology_stabilization_status"], "UNSTABLE_REVIEW_REQUIRED")

    def test_disagreement_and_saturation_outputs(self) -> None:
        matrix = json.loads((ROOT / "reports/gold125_label_disagreement_matrix.json").read_text(encoding="utf-8"))
        self.assertEqual(len(matrix), 43)
        self.assertEqual(sum(item["genuine_semantic_disagreement"] for item in matrix), 1)
        correction = [item for item in matrix if item["cause"] == "ANNOTATION_ERROR"]
        self.assertEqual([(item["trajectory"], item["step"]) for item in correction], [("MATH-GOLD-043", "s1")])

        saturation = json.loads((ROOT / "reports/gold125_ontology_v1_saturation.json").read_text(encoding="utf-8"))
        self.assertEqual([row["trajectories"] for row in saturation], [25, 50, 75, 100, 125])
        self.assertEqual([row["ontology_core_operations"] for row in saturation], [15, 17, 17, 17, 17])
        self.assertEqual([row["candidate_ontology_core_operations"] for row in saturation], [15, 17, 18, 18, 18])

        for name in (
            "core_operation_saturation_gold125.png",
            "new_core_operations_per_tranche_gold125.png",
            "core_topk_coverage_gold125.png",
        ):
            image = ROOT / "reports/figures" / name
            self.assertTrue(image.exists())
            self.assertEqual(image.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_amps_is_audit_only_and_source_copy_is_exact(self) -> None:
        audit = json.loads((ROOT / "reports/amps_khan_dataset_audit.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["rows"], 103059)
        self.assertEqual(audit["topic_count"], 721)
        self.assertEqual(audit["sha256"], "b48c40afd262a8ac587504bc3008a2b0d688c0144b5d9fddd083f0b576a5df41")
        self.assertTrue(REPO_AMPS.exists())
        self.assertEqual(hashlib.sha256(REPO_AMPS.read_bytes()).hexdigest(), audit["sha256"])
        if DESKTOP_AMPS.exists():
            self.assertEqual(hashlib.sha256(DESKTOP_AMPS.read_bytes()).hexdigest(), audit["sha256"])

        plan = json.loads((ROOT / "reports/amps_khan_candidate_selection_plan.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["status"], "PROSPECTIVE_ONLY_NOT_ANNOTATED")
        self.assertEqual(len(plan["candidates"]), 100)
        self.assertTrue(all(item["status"] == "PROSPECTIVE_ONLY_NOT_ANNOTATED" for item in plan["candidates"]))
        self.assertFalse((ROOT / "data/derived/amps_khan").exists())

    def test_hml_is_clean_pinned_and_read_only(self) -> None:
        actual = subprocess.check_output(["git", "-C", str(HML), "rev-parse", "HEAD"], text=True).strip()
        self.assertEqual(actual, PIN)
        self.assertEqual(subprocess.check_output(["git", "-C", str(HML), "status", "--porcelain"], text=True), "")
        writable = []
        for directory, dirnames, filenames in os.walk(HML):
            for name in dirnames + filenames:
                path = Path(directory) / name
                if path.is_symlink():
                    continue
                if path.stat().st_mode & 0o222:
                    writable.append(str(path))
        self.assertEqual(writable, [])

    def test_gold25_frozen_files_are_unchanged(self) -> None:
        freeze = json.loads((ROOT / "reports/gold25_freeze_hashes_2026-08-10.json").read_text(encoding="utf-8"))
        for relative, expected in freeze["files"].items():
            path = ROOT / relative
            self.assertTrue(path.exists(), relative)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected, relative)


if __name__ == "__main__":
    unittest.main()
