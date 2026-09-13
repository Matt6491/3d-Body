
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EX=json.loads((ROOT/"exercise-data"/"exercises.json").read_text())
REQUIRED={"id","name","movementPattern","equipment","difficulty","primaryMuscles","secondaryMuscles","stabilizers","typicalRepRange","loadType","notes"}
EXPECTED={
"Pushup","Incline pushup","Decline pushup","Bench press","Incline bench press","Chest fly",
"Overhead press","Lateral raise","Rear-delt raise","Triceps extension","Dip","Pull-up","Chin-up",
"Lat pulldown","Barbell row","Dumbbell row","Biceps curl","Hammer curl","Squat","Goblet squat",
"Lunge","Bulgarian split squat","Romanian deadlift","Deadlift","Hip thrust","Leg extension",
"Leg curl","Calf raise","Plank","Crunch","Hanging leg raise"
}
VALID_MUSCLES={
"pectoralisMajor","upperChest","anteriorDeltoid","lateralDeltoid","posteriorDeltoid","triceps",
"biceps","forearms","trapezius","latissimus","upperBack","abdominals","obliques","glutes",
"quadriceps","hamstrings","calves"
}

def test_catalog_contains_requested_exercises():
    assert EXPECTED <= {e["name"] for e in EX}
    assert len(EX)>=31

def test_catalog_schema_and_unique_ids():
    ids=[]
    for e in EX:
        assert REQUIRED <= e.keys()
        ids.append(e["id"])
        for field in ("primaryMuscles","secondaryMuscles","stabilizers"):
            assert set(e[field]) <= VALID_MUSCLES
        roles=e["primaryMuscles"]+e["secondaryMuscles"]+e["stabilizers"]
        assert len(roles)==len(set(roles)), f"duplicate muscle role in {e['id']}"
        assert e["primaryMuscles"], f"{e['id']} must have at least one primary muscle"
    assert len(ids)==len(set(ids))
