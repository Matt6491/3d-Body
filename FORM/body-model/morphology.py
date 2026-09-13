
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass(frozen=True)
class MorphRule:
    regions: tuple[str,...]
    axis_weights: tuple[float,float,float]
    surface: str
    gain: float

# Renderer-independent semantic deformation contract.
# axis_weights are relative local x/y/z expansion priorities; "surface" indicates
# the anatomical side on which bulging should occur instead of scaling a whole limb.
MORPH_RULES: Dict[str,MorphRule] = {
 "pectoralisMajor": MorphRule(("chestLeft","chestRight"),(.45,.25,1.0),"anterior",1.0),
 "upperChest": MorphRule(("upperChestLeft","upperChestRight"),(.40,.25,.85),"anterior",.8),
 "anteriorDeltoid": MorphRule(("shoulderLeft","shoulderRight"),(.25,.35,1.0),"anterior",.75),
 "lateralDeltoid": MorphRule(("shoulderLeft","shoulderRight"),(1.0,.45,.25),"lateral",.90),
 "posteriorDeltoid": MorphRule(("shoulderLeft","shoulderRight"),(.25,.35,1.0),"posterior",.75),
 "triceps": MorphRule(("upperArmLeft","upperArmRight"),(.35,.55,1.0),"posterior",.90),
 "biceps": MorphRule(("upperArmLeft","upperArmRight"),(.35,.55,1.0),"anterior",.90),
 "forearms": MorphRule(("forearmLeft","forearmRight"),(.6,.4,.6),"circumferential",.62),
 "trapezius": MorphRule(("trapezius",),(.55,.55,.75),"posterior-superior",.65),
 "latissimus": MorphRule(("latLeft","latRight"),(1.0,.35,.45),"posterior-lateral",.88),
 "upperBack": MorphRule(("upperBack",),(.65,.35,.8),"posterior",.70),
 "abdominals": MorphRule(("abdominalWall",),(.20,.45,1.0),"anterior",.55),
 "obliques": MorphRule(("obliqueLeft","obliqueRight"),(.8,.40,.25),"lateral",.52),
 "glutes": MorphRule(("gluteLeft","gluteRight"),(.45,.45,1.0),"posterior",.95),
 "quadriceps": MorphRule(("thighLeft","thighRight"),(.40,.55,1.0),"anterior",.90),
 "hamstrings": MorphRule(("thighLeft","thighRight"),(.40,.55,1.0),"posterior",.82),
 "calves": MorphRule(("calfLeft","calfRight"),(.55,.55,.75),"posterior-lateral",.72),
}

def build_morph_controls(muscles:Dict[str,float]) -> Dict[str,list[dict]]:
    """Convert normalized muscle parameters into local, directional morph controls."""
    out:Dict[str,list[dict]]={}
    for muscle,value in muscles.items():
        if value<=0 or muscle not in MORPH_RULES: continue
        rule=MORPH_RULES[muscle]
        amount=float(value)*rule.gain
        out[muscle]=[
          {"region":region,
           "surface":rule.surface,
           "scaleDelta":[round(amount*w,6) for w in rule.axis_weights]}
          for region in rule.regions
        ]
    return out
