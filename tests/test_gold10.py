#!/usr/bin/env python3
"""Executable invariant tests for the HML Reasoning Corpus V0 Gold-10."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hml_corpus.oracles import verify_canonical  # noqa: E402
from hml_corpus.size import measure_gold10  # noqa: E402
from hml_corpus.validation import EXPECTED_IDS, gold_paths, load_json, validate_gold10  # noqa: E402


PINNED_SHA = "164d1946e91216c093478132caa0d06427259682"


class Gold10Tests(unittest.TestCase):
    def test_trajectory_set_and_schema_invariants(self) -> None:
        errors = validate_gold10(ROOT)
        self.assertEqual(errors, [], "\n".join(errors))
        self.assertEqual({load_json(p)["example_id"] for p in gold_paths(ROOT)}, EXPECTED_IDS)

    def test_all_canonical_trajectories_are_verified_by_oracles(self) -> None:
        for path in gold_paths(ROOT):
            doc = load_json(path)
            ok, evidence = verify_canonical(doc)
            self.assertTrue(ok, f"{doc['example_id']}: {evidence}")
            self.assertEqual(doc["verification"]["canonical_status"], "VERIFIED")
            self.assertTrue(doc["goal_discharged"])

    def test_all_sixteen_reasoning_stage_ids_are_used(self) -> None:
        stages = set()
        for path in gold_paths(ROOT):
            doc = load_json(path)
            stages.update(doc["reasoning_stages_used"])
            for action in doc["actions"]:
                stages.update(action["reasoning_stages"])
        self.assertEqual(stages, set(range(1, 17)))

    def test_every_action_has_resolving_provenance(self) -> None:
        for path in gold_paths(ROOT):
            doc = load_json(path)
            state_ids = {state["id"] for state in doc["states"]}
            fact_ids = {
                claim["id"]
                for state in doc["states"]
                for field in ("facts", "assumptions", "goals", "subgoals", "unresolved_obligations", "epistemic_status")
                for claim in state[field]
            }
            for action in doc["actions"]:
                self.assertTrue(action["provenance"]["source_step"])
                self.assertIn(action["from_state"], state_ids)
                self.assertIn(action["to_state"], state_ids)
                for dependency in action["dependencies"]:
                    if dependency.startswith("fact:"):
                        self.assertIn(dependency, fact_ids)

    def test_no_semantic_gap_is_silently_marked_faithful(self) -> None:
        for path in gold_paths(ROOT):
            doc = load_json(path)
            if doc["semantic_gap_ids"]:
                self.assertNotEqual(doc["hml_status"], "FAITHFUL", doc["example_id"])
                for gap_id in doc["semantic_gap_ids"]:
                    self.assertTrue((ROOT / "reports" / "semantic_gaps" / f"{gap_id}.md").is_file())

    def test_hml_renderings_use_the_pinned_sha_and_compile(self) -> None:
        metadata = json.loads((ROOT / "schemas" / "project_metadata.json").read_text())
        self.assertEqual(metadata["hml_commit_sha"], PINNED_SHA)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "hml_core" / "src") + os.pathsep + env.get("PYTHONPATH", "")
        for path in gold_paths(ROOT):
            doc = load_json(path)
            hml_path = ROOT / doc["renderings"]["hml"]["path"]
            text = hml_path.read_text(encoding="utf-8")
            self.assertIn(PINNED_SHA, text, doc["example_id"])
            result = subprocess.run(
                [sys.executable, "-m", "hamiltonian_lang.cli", "check", str(hml_path)],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, f"{doc['example_id']}: {result.stderr}")
            expected = doc["renderings"]["hml"]["expected"]
            if expected == "fully_verified":
                self.assertIn("VERIFIED", result.stdout, doc["example_id"])
                self.assertIn("PROVED", result.stdout, doc["example_id"])

    def test_frozen_hml_submodule_is_clean_and_pinned(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tests" / "check_hml_core_pin.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_gold10_payload_size_is_reproducible(self) -> None:
        self.assertEqual(
            measure_gold10(ROOT),
            {
                "tokenizer": r"Unicode lexical tokens matching \w+|[^\w\s]",
                "file_count": 50,
                "utf8_bytes": 86028,
                "lexical_tokens": 28053,
                "canonical_trajectory_files": 10,
                "rendering_and_source_files": 40,
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
