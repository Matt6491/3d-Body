import unittest
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class TestExerciseData(unittest.TestCase):
    def test_exercise_database_completeness(self):
        edp = ROOT / "exercise-data" / "exercises.json"
        with open(edp, "r", encoding="utf-8") as f:
            exercises = json.load(f)

        self.assertGreaterEqual(len(exercises), 30)
        for ex in exercises:
            self.assertIn("id", ex)
            self.assertIn("name", ex)
            self.assertIn("primaryMuscles", ex)
            self.assertIn("secondaryMuscles", ex)
            self.assertIn("stabilizers", ex)
            self.assertIsInstance(ex["primaryMuscles"], list)

if __name__ == "__main__":
    unittest.main()
