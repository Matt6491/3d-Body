import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "adaptation-engine"))

from engine import MuscleAdaptationEngine, Profile, WorkoutItem, MUSCLES

class TestEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MuscleAdaptationEngine()

    def test_zero_weeks(self):
        p = Profile()
        item = WorkoutItem(exercise_id="pushup", sets=3, reps=10)
        r = self.engine.simulate(p, [item], 0)
        self.assertEqual(r.weeks, 0)
        self.assertTrue(all(v == 0.0 for v in r.muscles.values()))
        self.assertEqual(r.body_fat_delta, 0.0)

    def test_pushup_adaptation(self):
        p = Profile(experience="beginner", max_pushups=20)
        item = WorkoutItem(exercise_id="pushup", sets=4, reps=12, days_per_week=4)
        r = self.engine.simulate(p, [item], 12)
        self.assertGreater(r.muscles["pectoralisMajor"], 0)
        self.assertGreater(r.muscles["triceps"], 0)
        self.assertGreater(r.muscles["anteriorDeltoid"], 0)
        self.assertEqual(r.muscles["quadriceps"], 0)
        self.assertEqual(r.body_fat_delta, 0.0)

    def test_beginner_vs_advanced_growth(self):
        pb = Profile(experience="beginner")
        pa = Profile(experience="advanced")
        item = WorkoutItem(exercise_id="pushup", sets=4, reps=15, days_per_week=3)
        rb = self.engine.simulate(pb, [item], 12)
        ra = self.engine.simulate(pa, [item], 12)
        self.assertGreater(rb.muscles["pectoralisMajor"], ra.muscles["pectoralisMajor"])

    def test_starting_muscles_headroom(self):
        p_fresh = Profile(starting_muscles={})
        p_developed = Profile(starting_muscles={"pectoralisMajor": 0.8})
        item = WorkoutItem(exercise_id="pushup", sets=4, reps=15, days_per_week=3)
        r_fresh = self.engine.simulate(p_fresh, [item], 12)
        r_developed = self.engine.simulate(p_developed, [item], 12)
        self.assertGreater(r_fresh.muscles["pectoralisMajor"], r_developed.muscles["pectoralisMajor"])

    def test_diminishing_returns(self):
        p = Profile()
        item_mod = WorkoutItem(exercise_id="pushup", sets=3, reps=10, days_per_week=3)
        item_extreme = WorkoutItem(exercise_id="pushup", sets=15, reps=50, days_per_week=7)
        r_mod = self.engine.simulate(p, [item_mod], 12)
        r_extreme = self.engine.simulate(p, [item_extreme], 12)
        self.assertLess(r_extreme.muscles["pectoralisMajor"], self.engine.max_delta)

    def test_plateau_behavior(self):
        p = Profile()
        item = WorkoutItem(exercise_id="pushup", sets=4, reps=10, days_per_week=3)
        r12 = self.engine.simulate(p, [item], 12)
        r52 = self.engine.simulate(p, [item], 52)
        self.assertGreaterEqual(r52.muscles["pectoralisMajor"], r12.muscles["pectoralisMajor"])

if __name__ == "__main__":
    unittest.main()
