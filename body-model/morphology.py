MORPH_RULES = {
 "pectoralisMajor": (("chestLeft","chestRight"),(.45,.25,1.0),"anterior",1.0),
 "upperChest": (("upperChestLeft","upperChestRight"),(.40,.25,.85),"anterior",.8),
 "anteriorDeltoid": (("shoulderLeft","shoulderRight"),(.25,.35,1.0),"anterior",.75),
 "lateralDeltoid": (("shoulderLeft","shoulderRight"),(1.0,.45,.25),"lateral",.90),
 "posteriorDeltoid": (("shoulderLeft","shoulderRight"),(.25,.35,1.0),"posterior",.75),
 "triceps": (("upperArmLeft","upperArmRight"),(.35,.55,1.0),"posterior",.90),
 "biceps": (("upperArmLeft","upperArmRight"),(.35,.55,1.0),"anterior",.90),
 "forearms": (("forearmLeft","forearmRight"),(.6,.4,.6),"circumferential",.62),
 "trapezius": (("trapezius",),(.55,.55,.75),"posterior-superior",.65),
 "latissimus": (("latLeft","latRight"),(1.0,.35,.45),"posterior-lateral",.88),
 "upperBack": (("upperBack",),(.65,.35,.8),"posterior",.70),
 "abdominals": (("abdominalWall",),(.20,.45,1.0),"anterior",.55),
 "obliques": (("obliqueLeft","obliqueRight"),(.8,.40,.25),"lateral",.52),
 "glutes": (("gluteLeft","gluteRight"),(.45,.45,1.0),"posterior",.95),
 "quadriceps": (("thighLeft","thighRight"),(.40,.55,1.0),"anterior",.90),
 "hamstrings": (("thighLeft","thighRight"),(.40,.55,1.0),"posterior",.82),
 "calves": (("calfLeft","calfRight"),(.55,.55,.75),"posterior-lateral",.72),
}

def build_morph_controls(muscles: dict[str, float]) -> dict[str, list[dict]]:
    out = {}
    for muscle, value in muscles.items():
        if not value or value <= 0 or muscle not in MORPH_RULES:
            continue
        regions, axis_weights, surface, gain = MORPH_RULES[muscle]
        amount = value * gain
        out[muscle] = [
            {
                "region": r,
                "surface": surface,
                "scaleDelta": [round(amount * w, 6) for w in axis_weights],
            }
            for r in regions
        ]
    return out
