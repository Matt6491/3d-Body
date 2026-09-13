
import sys, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT/"adaptation-engine"))
from engine import MuscleAdaptationEngine,Profile,WorkoutItem,interpolate
EX=json.loads((ROOT/"exercise-data"/"exercises.json").read_text())
lookup={e["id"]:e for e in EX}
eng=MuscleAdaptationEngine(lookup)

def test_exercise_mapping():
    p=lookup["pushup"]
    assert p["primaryMuscles"]==["pectoralisMajor","triceps"]
    assert "anteriorDeltoid" in p["secondaryMuscles"]
    assert "quadriceps" not in p["primaryMuscles"]+p["secondaryMuscles"]+p["stabilizers"]

def test_timeline_interpolation():
    x=interpolate({"a":0},{"a":1},.5)
    assert abs(x["a"]-.5)<1e-9
    assert interpolate({"a":0},{"a":1},0)["a"]==0
    assert interpolate({"a":0},{"a":1},1)["a"]==1

def test_body_fat_constant():
    r=eng.simulate(Profile(),[WorkoutItem("pushup",sets=4,reps=15)],12)
    assert r.body_fat_delta==0

def test_untrained_unchanged_pushup():
    r=eng.simulate(Profile(),[WorkoutItem("pushup",sets=5,reps=20,days_per_week=7)],12)
    for m in ["quadriceps","hamstrings","calves","glutes","latissimus","biceps"]:
        assert r.muscles[m] == 0

def test_diminishing_returns_volume():
    p=Profile(max_pushups=25)
    low=eng.simulate(p,[WorkoutItem("pushup",sets=3,reps=10,days_per_week=3)],12).muscles["pectoralisMajor"]
    high=eng.simulate(p,[WorkoutItem("pushup",sets=10,reps=30,days_per_week=7)],12).muscles["pectoralisMajor"]
    assert high>low
    # >20x raw reps should produce far less than 20x modeled change.
    assert high < low*6

def test_beginner_responds_more_than_advanced():
    w=[WorkoutItem("bench-press",sets=4,reps=10,days_per_week=3,rir=2)]
    b=eng.simulate(Profile(experience="beginner"),w,12).muscles["pectoralisMajor"]
    a=eng.simulate(Profile(experience="advanced"),w,12).muscles["pectoralisMajor"]
    assert b>a

def test_100_pushups_day():
    p=Profile(age=35,sex="male",experience="intermediate",max_pushups=25)
    r=eng.simulate(p,[WorkoutItem("pushup",sets=5,reps=20,days_per_week=7,rir=2)],12)
    assert r.muscles["pectoralisMajor"]>0.02
    assert r.muscles["triceps"]>0.02
    assert r.muscles["anteriorDeltoid"]>0.005
    for m in ["quadriceps","hamstrings","calves","glutes","latissimus","biceps"]:
        assert r.muscles[m]<0.002

def test_multi_exercise_routine():
    r=eng.simulate(Profile(),[
      WorkoutItem("pushup",sets=4,reps=12,days_per_week=3),
      WorkoutItem("squat",sets=4,reps=10,days_per_week=3)
    ],12)
    assert r.muscles["pectoralisMajor"]>0 and r.muscles["quadriceps"]>0 and r.muscles["glutes"]>0
    assert r.muscles["calves"]==0

def test_zero_exercise_zero_adaptation():
    r=eng.simulate(Profile(),[],52)
    assert all(v==0 for v in r.muscles.values())

def test_time_plateaus():
    w=[WorkoutItem("pushup",sets=5,reps=20,days_per_week=7)]
    r12=eng.simulate(Profile(),w,12).muscles["pectoralisMajor"]
    r52=eng.simulate(Profile(),w,52).muscles["pectoralisMajor"]
    assert r52>r12
    assert (r52-r12) < r12


def test_starting_development_reduces_headroom():
    w=[WorkoutItem("bench-press",sets=4,reps=10,days_per_week=3,rir=2)]
    low=eng.simulate(Profile(starting_muscles={"pectoralisMajor":0.0}),w,12).muscles["pectoralisMajor"]
    developed=eng.simulate(Profile(starting_muscles={"pectoralisMajor":0.8}),w,12).muscles["pectoralisMajor"]
    assert low>developed>0


def test_100_pushups_stimulus_depends_on_current_capacity():
    w=[WorkoutItem("pushup",sets=5,reps=20,days_per_week=7,rir=2,reps_per_session=100)]
    lower_capacity=eng.simulate(Profile(max_pushups=15),w,12).muscles["pectoralisMajor"]
    high_capacity=eng.simulate(Profile(max_pushups=100),w,12).muscles["pectoralisMajor"]
    assert lower_capacity > high_capacity
    assert lower_capacity/high_capacity > 1.15
