import hashlib
import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lean_attestation" / "src"))

from lean_attestation.runtime import (
    CORPUS_SHA,
    EXPECTED_SPLIT_COUNTS,
    FORBIDDEN_INVENTED_FIELDS,
    HML_SHA,
    LEANDOJO_SHA,
    LEAN_BUILD_COMMIT,
    LEAN_CANONICAL_SHA256,
    LEAN_VERSION,
    MATHLIB_SHA,
    REPLAY_STATUSES,
    SOURCE_ARCHIVE_SHA256,
    compare_states,
    finalize_certificate,
    normalize_state,
    offline_lean_repo,
    install_offline_github_guard,
    exact_state_path,
    validate_certificate_shape,
)


class TestLeanAttestation(unittest.TestCase):
    def test_exact_environment_pins_are_full_and_frozen(self):
        self.assertEqual(LEAN_VERSION, "v4.10.0-rc1")
        self.assertEqual(LEAN_BUILD_COMMIT, "3b58e0649156")
        self.assertEqual(MATHLIB_SHA, "29dcec074de168ac2bf835a77ef68bbe069194c5")
        self.assertEqual(LEANDOJO_SHA, "abcfb72143ff3829e622418557e14c8b41b69a61")
        self.assertEqual(SOURCE_ARCHIVE_SHA256, "19b9a31968229d5bae4b959be9351d92740643d16a58c7f58f6d82795b8a98a4")
        self.assertEqual(LEAN_CANONICAL_SHA256, "8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869")
        self.assertEqual(HML_SHA, "84bf9897689b0ed78a2caaefc1db850d49b81260")
        self.assertEqual(CORPUS_SHA, "9d67e54450b9db897ee2ed20ec2e4cbbc16a3780")

    def test_state_comparison_integrity(self):
        self.assertEqual(compare_states("x\n⊢ P", "x\n⊢ P"), "EXACT_TEXT_MATCH")
        self.assertEqual(compare_states("x\r\n⊢ P\n", "x\n⊢ P"), "NORMALIZED_STATE_MATCH")
        self.assertEqual(compare_states("x : Nat\n⊢ P", "y : Nat\n⊢ P"), "MISMATCH")
        self.assertEqual(normalize_state("e\u0301\r\n"), "é")

    def test_no_semantic_equivalence_heuristic(self):
        self.assertEqual(compare_states("⊢ a = b", "⊢ b = a"), "MISMATCH")
        self.assertEqual(compare_states("h : P\n⊢ Q", "h₁ : P\n⊢ Q"), "MISMATCH")

    def test_runtime_error_statuses_remain_distinct(self):
        self.assertEqual(
            REPLAY_STATUSES,
            {"TRACE_ONLY", "REPLAY_PASS", "REPLAY_STATE_MISMATCH", "REPLAY_TACTIC_FAIL", "ENVIRONMENT_UNAVAILABLE", "UNSUPPORTED"},
        )

    def test_offline_repo_identity_does_not_require_github(self):
        try:
            repo = offline_lean_repo()
        except ModuleNotFoundError:
            self.skipTest("LeanDojo is not installed in the lightweight unit environment")
        self.assertEqual(repo.url, "https://github.com/leanprover-community/mathlib4")
        self.assertEqual(repo.commit, MATHLIB_SHA)
        self.assertEqual(repo.name, "mathlib4")

    def test_github_guard_blocks_unpinned_metadata_lookup(self):
        try:
            from github import Github
        except ModuleNotFoundError:
            self.skipTest("PyGithub is not installed in the lightweight unit environment")
        install_offline_github_guard()
        self.assertEqual(Github().get_repo("leanprover/lean4").name, "lean4")
        with self.assertRaises(RuntimeError):
            Github().get_repo("unplanned/repository")

    def test_nested_trace_list_is_not_treated_as_linear_prefix(self):
        tactics = [
            {"tactic": "outer", "state_before": "S0", "state_after": "S2"},
            {"tactic": "nested", "state_before": "S1", "state_after": "no goals"},
            {"tactic": "next", "state_before": "S2", "state_after": "S3"},
        ]
        self.assertIsNone(exact_state_path(tactics, 1))
        self.assertEqual(exact_state_path(tactics, 2), [0])

    def test_split_counts_and_identity(self):
        self.assertEqual(EXPECTED_SPLIT_COUNTS, {"TRAIN": 192882, "DEV": 24067, "FINAL": 24316})
        self.assertEqual(sum(EXPECTED_SPLIT_COUNTS.values()), 241265)

    def test_schema_has_required_contract_and_no_hml_fields(self):
        schema = json.loads((ROOT / "lean_attestation" / "schemas" / "lean_attestation_certificate.schema.json").read_text())
        required = set(schema["required"])
        for field in ("certificate_id", "recorded", "runtime", "replay_status", "before_match", "after_match", "attestation_code_sha"):
            self.assertIn(field, required)
        self.assertFalse(FORBIDDEN_INVENTED_FIELDS.intersection(schema["properties"]))

    def test_content_hash_excludes_only_timestamp_and_self_hash(self):
        certificate = self._certificate()
        first = finalize_certificate(certificate)
        first_hash = first["content_sha256_excluding_created_at"]
        second = dict(first)
        second["certificate_created_at"] = "2099-01-01T00:00:00Z"
        second["content_sha256_excluding_created_at"] = "0" * 64
        second = finalize_certificate(second)
        self.assertEqual(first_hash, second["content_sha256_excluding_created_at"])
        second["source_record_id"] = "changed"
        second["content_sha256_excluding_created_at"] = "0" * 64
        second = finalize_certificate(second)
        self.assertNotEqual(first_hash, second["content_sha256_excluding_created_at"])

    def test_certificate_shape_and_no_field_invention(self):
        certificate = finalize_certificate(self._certificate())
        validate_certificate_shape(certificate)
        self.assertFalse(FORBIDDEN_INVENTED_FIELDS.intersection(certificate))

    def test_no_hml_mutation_when_authority_is_available(self):
        root = os.environ.get("HML_FROZEN_PATH")
        if not root:
            self.skipTest("HML_FROZEN_PATH is not configured")
        path = Path(root)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path, text=True).strip()
        status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=path, text=True).strip()
        self.assertEqual(head, HML_SHA)
        self.assertEqual(status, "")
        writable_mask = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
        self.assertFalse(any(p.is_file() and p.stat().st_mode & writable_mask for p in path.rglob("*")))

    def _certificate(self):
        z = "0" * 64
        return {
            "schema_version": "lean-attestation-certificate-1.0.0",
            "certificate_id": "LEAN-ATT-" + "0" * 24,
            "source_record_id": "r",
            "source_record_sha256": z,
            "source_theorem_id": "T",
            "source_file": "Mathlib/T.lean",
            "source_split": "TRAIN",
            "source_official_split": "train",
            "transition_index": 0,
            "environment": {"lean_version": LEAN_VERSION, "lean_build_commit": LEAN_BUILD_COMMIT, "mathlib_sha": MATHLIB_SHA, "leandojo_version": "2.0.0", "leandojo_sha": LEANDOJO_SHA, "source_artifact_sha256": LEAN_CANONICAL_SHA256, "source_archive_sha256": SOURCE_ARCHIVE_SHA256},
            "recorded": {"state_before_raw_sha256": z, "state_before_normalized_sha256": z, "action": "rfl", "action_sha256": z, "state_after_raw_sha256": z, "state_after_normalized_sha256": z},
            "runtime": {"state_before_raw_sha256": z, "state_before_normalized_sha256": z, "action": "rfl", "action_sha256": z, "state_after_raw_sha256": z, "state_after_normalized_sha256": z},
            "replay_status": "REPLAY_PASS",
            "before_match": "EXACT_TEXT_MATCH",
            "after_match": "EXACT_TEXT_MATCH",
            "backend_result": {"result_type": "ProofFinished"},
            "runtime_io": {"stdout_sha256": None, "stderr_sha256": None, "protocol_result_sha256": z, "note": "test"},
            "runtime_environment_digest": z,
            "certificate_created_at": "2026-08-12T00:00:00Z",
            "attestation_code_sha": z,
            "content_sha256_excluding_created_at": z,
        }


if __name__ == "__main__":
    unittest.main()
