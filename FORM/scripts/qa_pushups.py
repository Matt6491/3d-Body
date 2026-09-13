
#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"adaptation-engine"))
from engine import MuscleAdaptationEngine,Profile,WorkoutItem
ex=json.loads((ROOT/"exercise-data"/"exercises.json").read_text())
eng=MuscleAdaptationEngine({x["id"]:x for x in ex})
profile=Profile(age=35,sex="male",experience="intermediate",max_pushups=25,recovery=.85,adherence=.95)
work=[WorkoutItem("pushup",sets=5,reps=20,days_per_week=7,rir=2)]
targets=["pectoralisMajor","triceps","anteriorDeltoid"]
unrelated=["quadriceps","hamstrings","calves","glutes","latissimus","biceps"]
print("FORM QA · 35M · 100 pushups/day")
print("weeks | chest | triceps | front delt | max unrelated | body-fat Δ")
for w in [0,2,4,8,12,26,39,52]:
    r=eng.simulate(profile,work,w)
    max_u=max(r.muscles[m] for m in unrelated)
    print(f"{w:>5} | {r.muscles['pectoralisMajor']:.4f} | {r.muscles['triceps']:.4f} | {r.muscles['anteriorDeltoid']:.4f} | {max_u:.4f} | {r.body_fat_delta:.1f}")
    assert all(r.muscles[m]>=0 for m in targets)
    assert max_u < .002
    assert r.body_fat_delta==0
r=eng.simulate(profile,work,12)
assert r.muscles["pectoralisMajor"]>r.muscles["anteriorDeltoid"]>0
print("PASS")
