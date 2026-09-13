
from __future__ import annotations
from typing import Literal
import sys, json, os, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.extend([str(ROOT/"adaptation-engine"),str(ROOT/"computer-vision"),str(ROOT/"body-model")])
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from engine import MuscleAdaptationEngine, Profile, WorkoutItem, MUSCLES
from pipeline import SilhouetteAnalyzer
from provider import get_body_model_provider
from .storage import InMemoryBodyRepository

EXERCISES=json.loads((ROOT/"exercise-data"/"exercises.json").read_text())
LOOKUP={e["id"]:e for e in EXERCISES}
engine=MuscleAdaptationEngine(LOOKUP)
analyzer=SilhouetteAnalyzer()
provider=get_body_model_provider(os.getenv("FORM_BODY_MODEL_PROVIDER","parametric-primitives"))
app=FastAPI(title="FORM API",version="0.1.0")
allowed_origins=[x.strip() for x in os.getenv("FORM_ALLOWED_ORIGINS","http://localhost:3000,http://127.0.0.1:3000").split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=allowed_origins,allow_credentials=False,allow_methods=["GET","POST","DELETE","OPTIONS"],allow_headers=["Content-Type","Authorization","X-Form-Session"])

# Prototype ephemeral repository: avoids persistence of sensitive photos.
repo=InMemoryBodyRepository()

class WorkoutRequest(BaseModel):
    exercise_id:str
    sets:int=Field(default=1,ge=1,le=30)
    reps:int=Field(default=10,ge=1,le=500)
    days_per_week:float=Field(default=3.0,gt=0,le=7)
    rir:float=Field(default=2.0,ge=0,le=10)
    load_factor:float=Field(default=1.0,gt=0,le=3.0)
    reps_per_session:int|None=Field(default=None,ge=1,le=5000)
    resistance_kg:float|None=Field(default=None,ge=0,le=1000)

class SimRequest(BaseModel):
    age:int=Field(default=35,ge=18,le=100)
    sex:Literal["male","female"]="male"
    experience:Literal["beginner","intermediate","advanced"]="beginner"
    recovery:float=Field(default=.85,ge=0,le=1)
    adherence:float=Field(default=.9,ge=0,le=1)
    maxPushups:int|None=Field(default=25,ge=1,le=500)
    startingMuscles:dict[str,float]=Field(default_factory=dict)
    weeks:float=Field(default=12,ge=0,le=52)
    workout:list[WorkoutRequest]

@app.get("/health")
def health(): return {"ok":True}
@app.get("/exercises")
def exercises(): return EXERCISES

@app.post("/analyze")
async def analyze(front:UploadFile=File(...),side:UploadFile=File(...),back:UploadFile=File(...),
                  age:int=Form(...),sex:str=Form(...),height_cm:float=Form(...),weight_kg:float=Form(...),
                  experience:str=Form(...),consent:bool=Form(...),adult_confirmed:bool=Form(...),
                  auto_delete_originals:bool=Form(True), exclude_face:bool=Form(True),
                  body_fat_estimate:float|None=Form(None), training_frequency:int|None=Form(None),
                  known_shoulder_width_cm:float|None=Form(None), known_waist_width_cm:float|None=Form(None),
                  known_hip_width_cm:float|None=Form(None)):
    if not consent: raise HTTPException(400,"Explicit photo-processing consent is required.")
    if not adult_confirmed or age<18: raise HTTPException(400,"FORM accepts adults age 18 or older only.")
    if sex not in ("male","female"): raise HTTPException(400,"biological sex must be male or female")
    if experience not in ("beginner","intermediate","advanced"): raise HTTPException(400,"invalid training experience")
    allowed={"image/jpeg","image/png","image/webp"}
    for upload in (front,side,back):
        if upload.content_type not in allowed:
            raise HTTPException(415,"Photos must be JPEG, PNG, or WebP.")
    blobs=[await x.read() for x in (front,side,back)]
    if any(len(b)>12_000_000 for b in blobs): raise HTTPException(413,"Each photo must be under 12 MB.")
    try: result=analyzer.analyze(*blobs,height_cm=height_cm,weight_kg=weight_kg)
    except Exception as e: raise HTTPException(422,f"Could not analyze photos: {e}")
    known={"shoulder_width_cm":known_shoulder_width_cm,"waist_width_cm":known_waist_width_cm,"hip_width_cm":known_hip_width_cm}
    for key,value in known.items():
        if value is not None:
            if not 10 <= value <= 80: raise HTTPException(400,f"{key} is outside the supported prototype range")
            result.measurements[key]=round(float(value),1)
    body=provider.fitBodyFromPhotos(result.__dict__,height_cm,weight_kg)
    if body_fat_estimate is not None:
        if not 3 <= body_fat_estimate <= 60: raise HTTPException(400,"Body-fat estimate must be between 3 and 60 percent.")
        provider.setBodyCompositionParameter(body,body_fat_estimate/100.0)
    if training_frequency is not None and not 0 <= training_frequency <= 14:
        raise HTTPException(400,"Training frequency must be between 0 and 14 sessions per week.")
    aid=repo.save_analysis(None,result.__dict__)
    bid=repo.save_body(None,provider.getMesh(body),{"age":age,"sex":sex,"experience":experience,
                    "trainingFrequency":training_frequency,"selfReportedBodyFat":body_fat_estimate})
    # blobs intentionally go out of scope; no original image store in local MVP.
    return {"analysisId":aid,"bodyId":bid,"analysis":result.__dict__,"body":repo.get_body(bid)["mesh"],
            "originalPhotosRetained":False,"faceAppearanceRetained":False,
            "privacy":{"requestedAutoDelete":auto_delete_originals,"excludeFace":exclude_face,"localModeAlwaysDiscardsOriginals":True}}

@app.get("/body/{body_id}")
def body(body_id:str):
    found=repo.get_body(body_id)
    if not found: raise HTTPException(404,"Body model not found")
    return found

@app.delete("/body/{body_id}")
def delete_body(body_id:str):
    return {"deleted":repo.delete_body(body_id)}

@app.delete("/analysis/{analysis_id}")
def delete_analysis(analysis_id:str):
    return {"deleted":repo.delete_analysis(analysis_id)}

@app.post("/simulate")
def simulate(req:SimRequest):
    items=[]
    for w in req.workout:
        if w.exercise_id not in LOOKUP: raise HTTPException(400,f"Unknown exercise: {w.exercise_id}")
        items.append(WorkoutItem(**w.model_dump()))
    p=Profile(age=req.age,sex=req.sex,experience=req.experience,recovery=req.recovery,adherence=req.adherence,max_pushups=req.maxPushups,
              starting_muscles={k:max(0.0,min(1.0,float(v))) for k,v in req.startingMuscles.items() if k in MUSCLES})
    r=engine.simulate(p,items,req.weeks)
    return {"weeks":r.weeks,"muscles":r.muscles,"bodyFatDelta":r.body_fat_delta}


@app.post("/simulate/timeline")
def simulate_timeline(req:SimRequest):
    items=[]
    for w in req.workout:
        if w.exercise_id not in LOOKUP:
            raise HTTPException(400,f"Unknown exercise: {w.exercise_id}")
        items.append(WorkoutItem(**w.model_dump()))
    p=Profile(age=req.age,sex=req.sex,experience=req.experience,recovery=req.recovery,adherence=req.adherence,max_pushups=req.maxPushups,
              starting_muscles={k:max(0.0,min(1.0,float(v))) for k,v in req.startingMuscles.items() if k in MUSCLES})
    checkpoints=[0,2,4,8,12,26,39,52]
    states=[]
    for weeks in checkpoints:
        r=engine.simulate(p,items,weeks)
        states.append({"weeks":weeks,"muscles":r.muscles,"bodyFatDelta":r.body_fat_delta})
    return {"checkpoints":states}

@app.get("/qa/pushups")
def qa_pushups(weeks:float=12):
    p=Profile(age=35,sex="male",experience="intermediate",max_pushups=25,recovery=.85,adherence=.95)
    item=WorkoutItem(exercise_id="pushup",sets=5,reps=20,days_per_week=7,rir=2)
    r=engine.simulate(p,[item],weeks)
    targeted=["pectoralisMajor","triceps","anteriorDeltoid"]
    unrelated=["quadriceps","hamstrings","calves","glutes","latissimus","biceps"]
    passed=all(r.muscles[x]>0 for x in targeted) and all(r.muscles[x]<.002 for x in unrelated) and r.body_fat_delta==0
    return {"passed":passed,"targeted":{x:r.muscles[x] for x in targeted},"unrelated":{x:r.muscles[x] for x in unrelated},"bodyFatDelta":r.body_fat_delta}
