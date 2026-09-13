import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "adaptation-engine"))

from engine import MuscleAdaptationEngine, Profile, WorkoutItem

def main():
    engine = MuscleAdaptationEngine()
    profile = Profile(age=35, sex="male", experience="intermediate", max_pushups=25, recovery=0.85, adherence=0.95)
    item = WorkoutItem(exercise_id="pushup", sets=5, reps=20, days_per_week=7, rir=2)

    for w in [2, 4, 8, 12, 26, 52]:
        r = engine.simulate(profile, [item], w)
        assert r.muscles["pectoralisMajor"] > 0, f"Chest did not grow at week {w}"
        assert r.muscles["triceps"] > 0, f"Triceps did not grow at week {w}"
        assert r.muscles["anteriorDeltoid"] > 0, f"Shoulders did not grow at week {w}"
        assert r.muscles["quadriceps"] == 0, f"Quads grew from pushups at week {w}"
        assert r.muscles["hamstrings"] == 0, f"Hamstrings grew from pushups at week {w}"
        assert r.muscles["calves"] == 0, f"Calves grew from pushups at week {w}"
        assert r.muscles["glutes"] == 0, f"Glutes grew from pushups at week {w}"
        assert r.muscles["latissimus"] == 0, f"Lats grew from pushups at week {w}"
        assert r.muscles["biceps"] == 0, f"Biceps grew from pushups at week {w}"
        assert r.body_fat_delta == 0, f"Body fat delta altered at week {w}"

    print("QA PUSHUP VERIFICATION: PASS across all checkpoints [2, 4, 8, 12, 26, 52] weeks.")

if __name__ == "__main__":
    main()
