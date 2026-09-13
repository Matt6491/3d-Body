from __future__ import annotations
import json
from dataclasses import dataclass, field
from math import exp
from pathlib import Path
from typing import Dict, List, Optional

MUSCLES = [
    "pectoralisMajor", "upperChest", "anteriorDeltoid", "lateralDeltoid", "posteriorDeltoid",
    "triceps", "biceps", "forearms", "trapezius", "latissimus", "upperBack", "abdominals",
    "obliques", "glutes", "quadriceps", "hamstrings", "calves"
]

@dataclass
class WorkoutItem:
    exercise_id: str
    sets: int = 1
    reps: int = 10
    days_per_week: float = 3.0
    rir: float = 2.0
    load_factor: float = 1.0
    reps_per_session: Optional[int] = None
    resistance_kg: Optional[float] = None

@dataclass
class Profile:
    age: int = 35
    sex: str = "male"
    experience: str = "beginner"
    recovery: float = 0.85
    adherence: float = 0.90
    max_pushups: Optional[int] = 25
    starting_muscles: Dict[str, float] = field(default_factory=dict)

@dataclass
class AdaptationResult:
    weeks: float
    muscles: Dict[str, float]
    body_fat_delta: float = 0.0
    debug: Dict[str, any] = field(default_factory=dict)

class MuscleAdaptationEngine:
    def __init__(self, exercise_data_path: Optional[Path] = None, config_path: Optional[Path] = None):
        root = Path(__file__).resolve().parent
        repo_root = root.parent
        edp = exercise_data_path or (repo_root / "exercise-data" / "exercises.json")
        if not edp.exists():
            edp = repo_root / "data" / "exercises.json"
        with open(edp, "r", encoding="utf-8") as f:
            self.exercises = json.load(f)
        self.exercise_lookup = {ex["id"]: ex for ex in self.exercises}

        cfg_file = config_path or (root / "config.json")
        with open(cfg_file, "r", encoding="utf-8") as f:
            self.cfg = json.load(f)

        self.role_coefficient = self.cfg["roleCoefficients"]
        self.level_response = self.cfg["experienceResponse"]
        self.max_delta = float(self.cfg["maxNormalizedMuscleDelta"])
        self.base_growth_scale = float(self.cfg["baseGrowthScale"])
        self.minimum_effective = float(self.cfg["minimumEffectiveWeeklyReps"])
        self.productive_midpoint = float(self.cfg["productiveVolumeMidpoint"])
        self.effort_quality_floor = float(self.cfg["effortQualityFloor"])
        self.recovery_overload_threshold = float(self.cfg["recoveryOverloadThresholdEffectiveReps"])
        self.recovery_overload_scale = float(self.cfg["recoveryOverloadScale"])

    @staticmethod
    def _effort_factor(item: WorkoutItem, profile: Profile) -> float:
        rir_factor = max(0.20, min(1.0, 1.05 - 0.16 * max(0.0, item.rir)))
        if item.exercise_id == "pushup" and profile.max_pushups:
            representative_reps = min(20, item.reps_per_session) if item.reps_per_session is not None else item.reps
            relative = min(1.0, representative_reps / max(1.0, profile.max_pushups))
            capacity_factor = 0.25 + 0.75 * (relative ** 0.55)
        else:
            capacity_factor = max(0.3, min(1.0, item.load_factor))
        return rir_factor * capacity_factor

    def _volume_response(self, weekly_effective_reps: float) -> float:
        if weekly_effective_reps <= self.minimum_effective:
            return 0.0
        if weekly_effective_reps <= 12:
            return (weekly_effective_reps - self.minimum_effective) / (60.0 - self.minimum_effective)
        return 0.20 + 0.80 * (1.0 - exp(-(weekly_effective_reps - 12.0) / self.productive_midpoint))

    def _recovery_penalty(self, days_per_week: float, weekly_effective_reps: float, recovery: float) -> float:
        density = days_per_week / 4.0
        overload = max(0.0, weekly_effective_reps - self.recovery_overload_threshold) / self.recovery_overload_scale
        penalty = 1.0 / (1.0 + 0.22 * density + 0.35 * overload)
        return max(0.50, min(1.0, penalty * (0.75 + 0.3 * recovery)))

    @staticmethod
    def _time_response(weeks: float, no_progressive_overload: bool = True) -> float:
        if weeks <= 0: return 0.0
        tau = 13.0 if no_progressive_overload else 20.0
        plateau = 1.0 - exp(-weeks / tau)
        if no_progressive_overload and weeks > 12:
            plateau *= 0.92 + 0.08 * exp(-(weeks - 12) / 20)
        return plateau

    def simulate(self, profile: Profile, workout: List[WorkoutItem], weeks: float) -> AdaptationResult:
        deltas = {m: 0.0 for m in MUSCLES}
        debug = {}
        if weeks <= 0:
            return AdaptationResult(weeks=weeks, muscles=deltas, body_fat_delta=0.0)

        for item in workout:
            ex = self.exercise_lookup[item.exercise_id]
            reps_session = item.reps_per_session if item.reps_per_session is not None else item.sets * item.reps
            effort = self._effort_factor(item, profile)
            weekly = reps_session * item.days_per_week * effort
            volume = self._volume_response(weekly)
            recovery = self._recovery_penalty(item.days_per_week, weekly, profile.recovery)
            time = self._time_response(weeks, no_progressive_overload=True)
            level = self.level_response[profile.experience]
            effort_quality = self.effort_quality_floor + (1.0 - self.effort_quality_floor) * effort
            base = self.base_growth_scale * level * volume * effort_quality * recovery * time * profile.adherence

            per = {}
            for role, key in (("primary", "primaryMuscles"), ("secondary", "secondaryMuscles"), ("stabilizer", "stabilizers")):
                for muscle in ex.get(key, []):
                    if muscle in deltas:
                        starting = max(0.0, min(1.0, profile.starting_muscles.get(muscle, 0.0)))
                        development_headroom = 1.0 - 0.35 * starting
                        contribution = base * self.role_coefficient[role] * development_headroom
                        deltas[muscle] += contribution
                        per[muscle] = per.get(muscle, 0) + contribution
            debug[item.exercise_id] = {
                "weekly_effective_reps": weekly,
                "effort": effort,
                "effort_quality": effortQuality if 'effortQuality' in locals() else effort_quality,
                "volume": volume,
                "recovery": recovery,
                "base": base,
                "muscles": per
            }

        deltas = {m: min(self.max_delta, self.max_delta * (1 - exp(-v / self.max_delta))) for m, v in deltas.items()}
        return AdaptationResult(weeks=weeks, muscles=deltas, body_fat_delta=0.0, debug=debug)

    @staticmethod
    def interpolate(start: Dict[str, float], end: Dict[str, float], t: float) -> Dict[str, float]:
        t = max(0.0, min(1.0, t))
        smooth = t * t * (3 - 2 * t)
        return {k: start.get(k, 0.0) + (end.get(k, 0.0) - start.get(k, 0.0)) * smooth for k in MUSCLES}
