
import sys
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT/"computer-vision"))
from pipeline import SilhouetteAnalyzer

def img(side=False):
    im=Image.new("RGB",(400,800),"white")
    d=ImageDraw.Draw(im)
    width=90 if side else 170
    d.ellipse((200-width//3,40,200+width//3,160),fill="gray")
    d.rounded_rectangle((200-width//2,150,200+width//2,500),30,fill="gray")
    d.rectangle((150,480,190,760),fill="gray"); d.rectangle((210,480,250,760),fill="gray")
    b=BytesIO(); im.save(b,"JPEG"); return b.getvalue()

def test_silhouette_analysis():
    a=SilhouetteAnalyzer().analyze(img(),img(True),img(),178,80)
    assert 35<a.measurements["shoulder_width_cm"]<60
    assert a.method=="local-silhouette-v2"
    assert "warning" in a.quality
    assert {"head","shoulders","chestRegion","waist","hips","upperArms","forearms","thighs","calves","feet"} <= set(a.landmarks["frontRegions"])
    assert "leftShoulder" in a.landmarks["frontCoarseJoints"]


def test_blank_image_rejected():
    im=Image.new("RGB",(400,800),"white"); b=BytesIO(); im.save(b,"JPEG")
    bad=b.getvalue()
    import pytest
    with pytest.raises(ValueError):
        SilhouetteAnalyzer().analyze(bad,bad,bad,178,80)
