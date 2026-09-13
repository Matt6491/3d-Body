import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "body-model"))

from morphology import MORPH_RULES, build_morph_controls

class TestMorphology(unittest.TestCase):
    def test_morph_rules_exist(self):
        self.assertEqual(len(MORPH_RULES), 17)
        self.assertIn("pectoralisMajor", MORPH_RULES)
        self.assertIn("quadriceps", MORPH_RULES)

    def test_build_morph_controls(self):
        muscles = {"pectoralisMajor": 0.05, "triceps": 0.03}
        controls = build_morph_controls(muscles)
        self.assertIn("pectoralisMajor", controls)
        self.assertIn("triceps", controls)
        self.assertEqual(len(controls["pectoralisMajor"]), 2)

if __name__ == "__main__":
    unittest.main()
