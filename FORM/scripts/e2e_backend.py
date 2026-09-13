
#!/usr/bin/env python3
from __future__ import annotations
import os,subprocess,sys,time
from io import BytesIO
from pathlib import Path
import httpx
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
PORT=8011
BASE=f"http://127.0.0.1:{PORT}"

def photo(side=False):
    im=Image.new("RGB",(400,800),"white");d=ImageDraw.Draw(im);w=90 if side else 170
    d.ellipse((200-w//3,40,200+w//3,160),fill=(105,105,105))
    d.rounded_rectangle((200-w//2,150,200+w//2,500),30,fill=(105,105,105))
    d.rectangle((155,480,190,760),fill=(105,105,105));d.rectangle((210,480,245,760),fill=(105,105,105))
    b=BytesIO();im.save(b,"JPEG");return b.getvalue()

def main():
    env=os.environ.copy();env["PYTHONUNBUFFERED"]="1"
    p=subprocess.Popen([sys.executable,"-m","uvicorn","backend.app.main:app","--host","127.0.0.1","--port",str(PORT)],
      cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
    try:
        with httpx.Client(timeout=5) as c:
            deadline=time.time()+12
            while time.time()<deadline:
                try:
                    if c.get(BASE+"/health").status_code==200:break
                except Exception:pass
                time.sleep(.2)
            else:raise RuntimeError("uvicorn did not become ready")
            files={"front":("front.jpg",photo(),"image/jpeg"),"side":("side.jpg",photo(True),"image/jpeg"),"back":("back.jpg",photo(),"image/jpeg")}
            data={"age":"35","sex":"male","height_cm":"178","weight_kg":"80","experience":"intermediate","consent":"true","adult_confirmed":"true","auto_delete_originals":"true"}
            up=c.post(BASE+"/analyze",files=files,data=data);up.raise_for_status();uj=up.json()
            assert uj["originalPhotosRetained"] is False
            workout=[{"exercise_id":"pushup","sets":5,"reps":20,"days_per_week":7,"rir":2}]
            sim=c.post(BASE+"/simulate/timeline",json={"age":35,"sex":"male","experience":"intermediate","maxPushups":25,"weeks":52,"workout":workout});sim.raise_for_status()
            end=sim.json()["checkpoints"][-1]
            assert end["muscles"]["pectoralisMajor"]>0 and end["muscles"]["quadriceps"]==0 and end["bodyFatDelta"]==0
            assert c.delete(BASE+f"/body/{uj['bodyId']}").json()["deleted"] is True
            print("E2E PASS: upload -> reconstruct -> timeline -> targeted adaptation -> delete")
            print(f"12M chest={end['muscles']['pectoralisMajor']:.4f}, quad={end['muscles']['quadriceps']:.4f}, bodyFatDelta={end['bodyFatDelta']}")
    finally:
        p.terminate()
        try:p.wait(timeout=3)
        except subprocess.TimeoutExpired:p.kill()

if __name__=="__main__":main()
