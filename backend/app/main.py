from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from adaptation_engine.engine import MuscleAdaptationEngine, WorkoutItem, Profile
from body_model.provider import ParametricPrimitiveBodyProvider
from computer_vision.pipeline import SilhouetteAnalyzer
from backend.app.storage import InMemoryBodyRepository

# Also support hyphenated directory names:
try:
    import adaptation_engine.engine
except ImportError:
    pass

app = FastAPI(title="FORM API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = MuscleAdaptationEngine()
provider = ParametricPrimitiveBodyProvider()
analyzer = SilhouetteAnalyzer()
repo = InMemoryBodyRepository()

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 10 * 1024 * 1024

class RoutineIn(BaseModel):
    exercise_id: str
    sets: int = Field(default=1, ge=1, le=50)
    reps: int = Field(default=10, ge=1, le=500)
    days_per_week: float = Field(default=3.0, ge=0.5, le=7.0)
    rir: float = Field(default=2.0, ge=0.0, le=5.0)
    reps_per_session: Optional[int] = Field(default=None, ge=1, le=5000)
    resistance_kg: Optional[float] = Field(default=None, ge=0.0, le=500.0)

class SimulateIn(BaseModel):
    age: int = Field(default=35, ge=18, le=100)
    sex: str = "male"
    experience: str = "beginner"
    recovery: float = Field(default=0.85, ge=0.1, le=1.0)
    adherence: float = Field(default=0.90, ge=0.1, le=1.0)
    max_pushups: Optional[int] = Field(default=25, ge=0, le=200)
    starting_muscles: dict[str, float] = Field(default_factory=dict)
    weeks: float = Field(default=12.0, ge=0.0, le=104.0)
    workout: List[RoutineIn]

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/exercises")
def exercises():
    edp = ROOT / "exercise-data" / "exercises.json"
    if not edp.exists():
        edp = ROOT / "data" / "exercises.json"
    with open(edp, "r", encoding="utf-8") as f:
        return json.load(f)

async def _validate_upload(name: str, file: UploadFile) -> bytes:
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail=f"{name} must be JPEG, PNG, or WebP.")
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail=f"{name} photo file is empty.")
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=400, detail=f"{name} photo exceeds 10MB.")
    return content

@app.post("/analyze")
async def analyze(
    front: UploadFile = File(...),
    side: Optional[UploadFile] = File(None),
    back: Optional[UploadFile] = File(None),
    consent: bool = Form(...),
    adult_confirmed: bool = Form(...),
    age: int = Form(35),
    sex: str = Form("male"),
    height_cm: float = Form(178.0),
    weight_kg: float = Form(80.0),
    experience: str = Form("beginner"),
    body_fat_estimate: Optional[float] = Form(None),
    training_frequency: Optional[int] = Form(None),
    auto_delete_originals: bool = Form(True),
    exclude_face: bool = Form(True),
    known_shoulder_width_cm: Optional[float] = Form(None),
    known_waist_width_cm: Optional[float] = Form(None),
    known_hip_width_cm: Optional[float] = Form(None)
):
    if not consent:
        raise HTTPException(status_code=400, detail="Explicit photo-processing consent is required.")
    if not adult_confirmed or age < 18:
        raise HTTPException(status_code=400, detail="FORM accepts adults age 18 or older only.")

    if not front:
        raise HTTPException(status_code=400, detail="Front photo is required.")
    bf = await _validate_upload("front", front)

    bs = None
    if side and side.filename:
        bs = await _validate_upload("side", side)

    bb = None
    if back and back.filename:
        bb = await _validate_upload("back", back)

    try:
        res = analyzer.analyze(bf, bs, bb, height_cm, weight_kg)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if known_shoulder_width_cm is not None:
        res.measurements["shoulder_width_cm"] = known_shoulder_width_cm
    if known_waist_width_cm is not None:
        res.measurements["waist_width_cm"] = known_waist_width_cm
    if known_hip_width_cm is not None:
        res.measurements["hip_width_cm"] = known_hip_width_cm

    bf_param = body_fat_estimate / 100.0 if body_fat_estimate is not None else 0.22
    body_state = provider.fit_baseline(res.measurements, body_fat=bf_param)

    aid = repo.save_analysis(None, res.__dict__)
    bid = repo.save_body(None, body_state.__dict__, {
        "age": age, "sex": sex, "experience": experience,
        "training_frequency": training_frequency, "self_reported_body_fat": body_fat_estimate
    })

    return {
        "analysisId": aid,
        "bodyId": bid,
        "analysis": res.__dict__,
        "body": body_state.__dict__,
        "originalPhotosRetained": False,
        "faceAppearanceRetained": False,
        "privacy": {
            "requestedAutoDelete": auto_delete_originals,
            "excludeFace": exclude_face,
            "localModeAlwaysDiscardsOriginals": True
        }
    }

@app.get("/body/{body_id}")
def get_body(body_id: str):
    b = repo.get_body(body_id)
    if not b:
        raise HTTPException(status_code=404, detail="Body model not found")
    return b

@app.delete("/body/{body_id}")
def delete_body(body_id: str):
    return {"deleted": repo.delete_body(body_id)}

@app.delete("/analysis/{analysis_id}")
def delete_analysis(analysis_id: str):
    return {"deleted": repo.delete_analysis(analysis_id)}

@app.post("/simulate")
def simulate(req: SimulateIn):
    p = Profile(
        age=req.age, sex=req.sex, experience=req.experience,
        recovery=req.recovery, adherence=req.adherence,
        max_pushups=req.max_pushups, starting_muscles=req.starting_muscles
    )
    items = [WorkoutItem(**i.model_dump()) for i in req.workout]
    r = engine.simulate(p, items, req.weeks)
    return {
        "weeks": r.weeks,
        "muscles": r.muscles,
        "bodyFatDelta": r.body_fat_delta,
        "debug": r.debug
    }

@app.post("/simulate/timeline")
def simulate_timeline(req: SimulateIn):
    checkpoints = [0, 2, 4, 8, 12, 26, 39, 52]
    p = Profile(
        age=req.age, sex=req.sex, experience=req.experience,
        recovery=req.recovery, adherence=req.adherence,
        max_pushups=req.max_pushups, starting_muscles=req.starting_muscles
    )
    items = [WorkoutItem(**i.model_dump()) for i in req.workout]
    states = []
    for w in checkpoints:
        r = engine.simulate(p, items, w)
        states.append({"weeks": w, "muscles": r.muscles, "bodyFatDelta": r.body_fat_delta})
    return {"checkpoints": states}

@app.get("/qa/pushups")
def qa_pushups(weeks: float = 12):
    p = Profile(age=35, sex="male", experience="intermediate", max_pushups=25, recovery=0.85, adherence=0.95)
    item = WorkoutItem(exercise_id="pushup", sets=5, reps=20, days_per_week=7, rir=2)
    r = engine.simulate(p, [item], weeks)
    targeted = ["pectoralisMajor", "triceps", "anteriorDeltoid"]
    unrelated = ["quadriceps", "hamstrings", "calves", "glutes", "latissimus", "biceps"]
    passed = all(r.muscles[x] > 0 for x in targeted) and all(r.muscles[x] < 0.002 for x in unrelated) and r.body_fat_delta == 0
    return {
        "passed": passed,
        "targeted": {k: r.muscles[k] for k in targeted},
        "unrelated": {k: r.muscles[k] for k in unrelated},
        "bodyFatDelta": r.body_fat_delta
    }
