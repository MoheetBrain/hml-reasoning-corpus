import os
import subprocess
import unittest
from pathlib import Path

from synthetic_factory.authority import assert_authority


class AuthorityTests(unittest.TestCase):
    def test_all_authority_gates(self):
        authority = assert_authority()
        self.assertEqual(authority["status"], "AUTHORITY_VERIFIED")
        self.assertEqual(authority["hml"]["writable_file_count"], 0)
        self.assertTrue(authority["hml"]["working_tree_clean"])
        self.assertTrue(authority["lean_canonical"]["reconciles_exactly"])

    def test_hml_checkout_remains_byte_for_byte_git_clean(self):
        root = Path(os.environ["HML_FROZEN_PATH"])
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
        ).stdout
        self.assertEqual(status, "")


if __name__ == "__main__":
    unittest.main()
