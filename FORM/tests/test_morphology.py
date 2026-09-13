
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"body-model"))
from morphology import MORPH_RULES,build_morph_controls

def test_directional_anatomy_rules():
    assert MORPH_RULES["biceps"].surface=="anterior"
    assert MORPH_RULES["triceps"].surface=="posterior"
    assert MORPH_RULES["pectoralisMajor"].surface=="anterior"
    assert MORPH_RULES["latissimus"].surface=="posterior-lateral"
    assert MORPH_RULES["quadriceps"].surface=="anterior"
    assert MORPH_RULES["hamstrings"].surface=="posterior"
    assert MORPH_RULES["glutes"].surface=="posterior"

def test_untrained_regions_do_not_get_controls():
    c=build_morph_controls({"pectoralisMajor":.1,"triceps":.08,"quadriceps":0.0,"glutes":0.0})
    assert set(c)=={"pectoralisMajor","triceps"}
    assert all(x["region"].startswith("chest") for x in c["pectoralisMajor"])
    assert all(x["region"].startswith("upperArm") for x in c["triceps"])

def test_lateral_delt_prioritizes_width():
    c=build_morph_controls({"lateralDeltoid":.1})["lateralDeltoid"][0]["scaleDelta"]
    assert c[0] > c[1] > c[2]

def test_growth_amount_is_monotonic():
    a=build_morph_controls({"biceps":.05})["biceps"][0]["scaleDelta"]
    b=build_morph_controls({"biceps":.10})["biceps"][0]["scaleDelta"]
    assert all(y>x for x,y in zip(a,b))
