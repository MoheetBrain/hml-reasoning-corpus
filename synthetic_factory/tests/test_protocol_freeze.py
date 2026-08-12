import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProtocolFreezeTests(unittest.TestCase):
    def test_later_stages_are_disabled(self):
        protocol = (ROOT / "protocol.yaml").read_text(encoding="utf-8")
        self.assertIn("stage1000:\n    enabled: false", protocol)
        self.assertIn("stage10000:\n    enabled: false", protocol)
        self.assertIn("preserve_unresolved: true", protocol)


if __name__ == "__main__":
    unittest.main()
