
import sys
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.main import app
from fastapi.testclient import TestClient
client=TestClient(app)

def body_img(side=False):
    im=Image.new("RGB",(400,800),"white"); d=ImageDraw.Draw(im); w=90 if side else 170
    d.ellipse((200-w//3,40,200+w//3,160),fill=(100,100,100))
    d.rounded_rectangle((200-w//2,150,200+w//2,500),30,fill=(100,100,100))
    d.rectangle((155,480,190,760),fill=(100,100,100)); d.rectangle((210,480,245,760),fill=(100,100,100))
    b=BytesIO(); im.save(b,"JPEG"); return b.getvalue()

def upload_payload(age="35",adult="true",consent="true"):
    files={"front":("f.jpg",body_img(),"image/jpeg"),"side":("s.jpg",body_img(True),"image/jpeg"),"back":("b.jpg",body_img(),"image/jpeg")}
    data={"age":age,"sex":"male","height_cm":"178","weight_kg":"80","experience":"intermediate",
          "consent":consent,"adult_confirmed":adult,"auto_delete_originals":"true"}
    return files,data

def test_health():
    assert client.get("/health").json()=={"ok":True}

def test_adult_consent_required():
    files,data=upload_payload(age="17",adult="false")
    assert client.post("/analyze",files=files,data=data).status_code==400
    files,data=upload_payload(consent="false")
    assert client.post("/analyze",files=files,data=data).status_code==400

def test_upload_reconstruct_and_delete():
    files,data=upload_payload()
    r=client.post("/analyze",files=files,data=data)
    assert r.status_code==200
    j=r.json()
    assert j["originalPhotosRetained"] is False
    assert j["analysis"]["quality"]["fullBodyValidated"] is True
    body_id=j["bodyId"]
    assert client.get(f"/body/{body_id}").status_code==200
    assert client.delete(f"/body/{body_id}").json()["deleted"] is True
    assert client.get(f"/body/{body_id}").status_code==404

def test_timeline_bodyfat_constant_and_targeting():
    payload={"age":35,"sex":"male","experience":"intermediate","maxPushups":25,"weeks":52,
             "workout":[{"exercise_id":"pushup","sets":5,"reps":20,"days_per_week":7,"rir":2}]}
    r=client.post("/simulate/timeline",json=payload)
    assert r.status_code==200
    states=r.json()["checkpoints"]
    assert [s["weeks"] for s in states]==[0,2,4,8,12,26,39,52]
    assert all(s["bodyFatDelta"]==0 for s in states)
    assert states[-1]["muscles"]["pectoralisMajor"]>states[2]["muscles"]["pectoralisMajor"]>0
    assert states[-1]["muscles"]["quadriceps"]==0

def test_qa_endpoint():
    q=client.get("/qa/pushups?weeks=12").json()
    assert q["passed"] is True
    assert all(v==0 for v in q["unrelated"].values())


def test_simulation_validation_rejects_bad_values():
    bad={"age":17,"sex":"male","experience":"intermediate","weeks":12,"workout":[]}
    assert client.post("/simulate",json=bad).status_code==422
    bad={"age":35,"sex":"male","experience":"intermediate","weeks":99,"workout":[]}
    assert client.post("/simulate",json=bad).status_code==422
    bad={"age":35,"sex":"male","experience":"intermediate","weeks":12,
         "workout":[{"exercise_id":"pushup","sets":1,"reps":10,"days_per_week":9}]}
    assert client.post("/simulate",json=bad).status_code==422

def test_unknown_exercise_rejected():
    payload={"age":35,"sex":"male","experience":"intermediate","weeks":12,
             "workout":[{"exercise_id":"teleport-curl","sets":1,"reps":10,"days_per_week":3}]}
    assert client.post("/simulate",json=payload).status_code==400


def test_known_measurement_overrides_silhouette_estimate():
    files,data=upload_payload()
    data["known_shoulder_width_cm"]="48.5"
    data["known_waist_width_cm"]="33.0"
    r=client.post("/analyze",files=files,data=data)
    assert r.status_code==200
    m=r.json()["analysis"]["measurements"]
    assert m["shoulder_width_cm"]==48.5
    assert m["waist_width_cm"]==33.0
