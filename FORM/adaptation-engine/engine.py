
from __future__ import annotations
from dataclasses import dataclass, field
from math import exp, log1p
from typing import Dict, Iterable, Literal
from pathlib import Path
import json

MUSCLES = (
    "pectoralisMajor","upperChest","anteriorDeltoid","lateralDeltoid","posteriorDeltoid",
    "triceps","biceps","forearms","trapezius","latissimus","upperBack","abdominals",
    "obliques","glutes","quadriceps","hamstrings","calves"
)


@dataclass(frozen=True)
class WorkoutItem:
    exercise_id: str
    sets: int = 1
    reps: int = 10
    days_per_week: float = 3.0
    rir: float = 2.0
    load_factor: float = 1.0
    reps_per_session: int | None = None
    resistance_kg: float | None = None

@dataclass
class Profile:
    age: int = 35
    sex: Literal["male","female"] = "male"
    experience: Literal["beginner","intermediate","advanced"] = "beginner"
    recovery: float = 0.85
    adherence: float = 0.9
    max_pushups: int | None = 25
    starting_muscles: Dict[str,float] = field(default_factory=dict)

@dataclass
class AdaptationResult:
    weeks: float
    muscles: Dict[str,float]
    body_fat_delta: float = 0.0
    debug: Dict[str,dict] = field(default_factory=dict)

class MuscleAdaptationEngine:
    """Deterministic, bounded training-only adaptation model.

    Output values are normalized development deltas, not medical measurements.
    Body composition is intentionally separated and remains unchanged here.
    """
    def __init__(self, exercise_lookup: Dict[str,dict], config:dict|None=None):
        self.exercise_lookup = exercise_lookup
        if config is None:
            config=json.loads((Path(__file__).with_name("config.json")).read_text())
        self.config=config
        self.level_response=config["experienceResponse"]
        self.role_coefficient=config["roleCoefficients"]
        self.max_delta=float(config["maxNormalizedMuscleDelta"])
        self.base_growth_scale=float(config["baseGrowthScale"])
        self.minimum_effective=float(config["minimumEffectiveWeeklyReps"])
        self.productive_midpoint=float(config["productiveVolumeMidpoint"])
        self.effort_quality_floor=float(config.get("effortQualityFloor",0.65))
        self.recovery_overload_threshold=float(config.get("recoveryOverloadThresholdEffectiveReps",350))
        self.recovery_overload_scale=float(config.get("recoveryOverloadScale",500))

    @staticmethod
    def _effort_factor(item: WorkoutItem, profile: Profile) -> float:
        # RIR -> challenging sets get more stimulus, very easy work gets less.
        rir_factor = max(0.20, min(1.0, 1.05 - 0.16 * max(0.0, item.rir)))
        if item.exercise_id == "pushup" and profile.max_pushups:
            # In SIMPLE mode reps_per_session is a daily/session target rather than a
            # prescriptive set size. Use a nominal 20-rep working bout to distinguish
            # a user whose max is 15 from one whose max is 100 without pretending we
            # know how they distribute all 100 reps. STRUCTURED mode uses actual set reps.
            representative_reps = min(20, item.reps_per_session) if item.reps_per_session is not None else item.reps
            relative = min(1.0, representative_reps / max(1.0, profile.max_pushups))
            capacity_factor = 0.25 + 0.75 * (relative ** 0.55)
        else:
            capacity_factor = max(0.3, min(1.0, item.load_factor))
        return rir_factor * capacity_factor

    def _volume_response(self, weekly_effective_reps: float) -> float:
        # Minimum effective stimulus + productive range + diminishing returns.
        if weekly_effective_reps <= self.minimum_effective:
            return 0.0
        if weekly_effective_reps <= 12:
            return (weekly_effective_reps-self.minimum_effective)/(60.0-self.minimum_effective)
        # Saturating curve: added work gives progressively smaller modeled benefit.
        return 0.20 + 0.80 * (1.0 - exp(-(weekly_effective_reps - 12.0)/self.productive_midpoint))

    def _recovery_penalty(self, days_per_week: float, weekly_effective_reps: float, recovery: float) -> float:
        density = days_per_week / 4.0
        overload = max(0.0, weekly_effective_reps - self.recovery_overload_threshold) / self.recovery_overload_scale
        penalty = 1.0 / (1.0 + 0.22*density + 0.35*overload)
        return max(0.50, min(1.0, penalty * (0.75 + 0.3*recovery)))

    @staticmethod
    def _time_response(weeks: float, no_progressive_overload: bool = True) -> float:
        if weeks <= 0: return 0.0
        # Fast early adaptation, slowing toward a bounded plateau.
        tau = 13.0 if no_progressive_overload else 20.0
        plateau = 1.0 - exp(-weeks/tau)
        # repeated-bout effect for identical training after ~12 weeks
        if no_progressive_overload and weeks > 12:
            plateau *= 0.92 + 0.08*exp(-(weeks-12)/20)
        return plateau

    def simulate(self, profile: Profile, workout: Iterable[WorkoutItem], weeks: float) -> AdaptationResult:
        deltas = {m:0.0 for m in MUSCLES}
        debug={}
        if weeks <= 0:
            return AdaptationResult(weeks=weeks,muscles=deltas,body_fat_delta=0.0)
        for item in workout:
            ex=self.exercise_lookup[item.exercise_id]
            reps_session = item.reps_per_session if item.reps_per_session is not None else item.sets*item.reps
            effort=self._effort_factor(item,profile)
            weekly=reps_session*item.days_per_week*effort
            volume=self._volume_response(weekly)
            recovery=self._recovery_penalty(item.days_per_week,weekly,profile.recovery)
            time=self._time_response(weeks, no_progressive_overload=True)
            level=self.level_response[profile.experience]
            effort_quality=self.effort_quality_floor+(1.0-self.effort_quality_floor)*effort
            base=self.base_growth_scale*level*volume*effort_quality*recovery*time*profile.adherence
            per={}
            for role,key in (("primary","primaryMuscles"),("secondary","secondaryMuscles"),("stabilizer","stabilizers")):
                for muscle in ex.get(key,[]):
                    if muscle in deltas:
                        starting=max(0.0,min(1.0,profile.starting_muscles.get(muscle,0.0)))
                        development_headroom=1.0-0.35*starting
                        contribution=base*self.role_coefficient[role]*development_headroom
                        deltas[muscle]+=contribution
                        per[muscle]=per.get(muscle,0)+contribution
            debug[item.exercise_id]={"weekly_effective_reps":weekly,"effort":effort,"effort_quality":effort_quality,"volume":volume,"recovery":recovery,"base":base,"muscles":per}
        # Multi-exercise combination saturates rather than stacking without bound.
        deltas={m: min(self.max_delta, self.max_delta*(1-exp(-v/self.max_delta))) for m,v in deltas.items()}
        return AdaptationResult(weeks=weeks,muscles=deltas,body_fat_delta=0.0,debug=debug)

def interpolate(start: Dict[str,float], end: Dict[str,float], t: float)->Dict[str,float]:
    t=max(0.0,min(1.0,t))
    # smoothstep avoids abrupt endpoint motion
    s=t*t*(3-2*t)
    return {k:start.get(k,0)+(end.get(k,0)-start.get(k,0))*s for k in set(start)|set(end)}
