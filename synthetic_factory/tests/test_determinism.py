import hashlib
import tempfile
import unittest
from pathlib import Path

from synthetic_factory.generate import write_stage100


ROOT = Path(__file__).resolve().parents[1]


class DeterminismTests(unittest.TestCase):
    def test_regeneration_is_byte_identical(self):
        canonical = ROOT / "data/stage100/canonical_pairs.jsonl"
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "canonical_pairs.jsonl"
            write_stage100(output=candidate)
            self.assertEqual(
                hashlib.sha256(canonical.read_bytes()).hexdigest(),
                hashlib.sha256(candidate.read_bytes()).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
