import { MuscleKey, MUSCLES, Exercise, MuscleValues, emptyMuscles } from "./types";
import exercisesData from "@/data/exercises.json";

export interface WorkoutItem {
  exercise_id: string;
  sets?: number;
  reps?: number;
  days_per_week?: number;
  rir?: number;
  load_factor?: number;
  reps_per_session?: number;
  resistance_kg?: number;
}

export interface Profile {
  age?: number;
  sex?: "male" | "female";
  experience?: "beginner" | "intermediate" | "advanced";
  recovery?: number;
  adherence?: number;
  max_pushups?: number;
  starting_muscles?: Record<string, number>;
}

export interface AdaptationResult {
  weeks: number;
  muscles: MuscleValues;
  body_fat_delta: number;
  debug?: Record<string, any>;
}

const DEFAULT_CONFIG = {
  roleCoefficients: {
    primary: 1.0,
    secondary: 0.48,
    stabilizer: 0.16,
  },
  experienceResponse: {
    beginner: 1.0,
    intermediate: 0.72,
    advanced: 0.46,
  },
  maxNormalizedMuscleDelta: 0.34,
  baseGrowthScale: 0.22,
  minimumEffectiveWeeklyReps: 4,
  productiveVolumeMidpoint: 100,
  effortQualityFloor: 0.45,
  recoveryOverloadThresholdEffectiveReps: 350,
  recoveryOverloadScale: 500,
};

export class MuscleAdaptationEngine {
  private exerciseLookup: Record<string, Exercise>;
  private config = DEFAULT_CONFIG;

  constructor(exercises?: Exercise[]) {
    const list = exercises || (exercisesData as Exercise[]);
    this.exerciseLookup = Object.fromEntries(list.map((e) => [e.id, e]));
  }

  private effortFactor(item: WorkoutItem, profile: Profile): number {
    const rir = item.rir ?? 2.0;
    const rirFactor = Math.max(0.2, Math.min(1.0, 1.05 - 0.16 * Math.max(0.0, rir)));

    if (item.exercise_id === "pushup" && profile.max_pushups) {
      const repTarget = item.reps_per_session !== undefined ? item.reps_per_session : (item.reps ?? 10);
      const representativeReps = Math.min(20, repTarget);
      const relative = Math.min(1.0, representativeReps / Math.max(1.0, profile.max_pushups));
      const capacityFactor = 0.25 + 0.75 * Math.pow(relative, 0.55);
      return rirFactor * capacityFactor;
    } else {
      const loadFactor = item.load_factor ?? 1.0;
      const capacityFactor = Math.max(0.3, Math.min(1.0, loadFactor));
      return rirFactor * capacityFactor;
    }
  }

  private volumeResponse(weeklyEffectiveReps: number): number {
    if (weeklyEffectiveReps <= this.config.minimumEffectiveWeeklyReps) {
      return 0.0;
    }
    if (weeklyEffectiveReps <= 12) {
      return (
        (weeklyEffectiveReps - this.config.minimumEffectiveWeeklyReps) /
        (60.0 - this.config.minimumEffectiveWeeklyReps)
      );
    }
    return (
      0.2 +
      0.8 * (1.0 - Math.exp(-(weeklyEffectiveReps - 12.0) / this.config.productiveVolumeMidpoint))
    );
  }

  private recoveryPenalty(
    daysPerWeek: number,
    weeklyEffectiveReps: number,
    recovery: number
  ): number {
    const density = daysPerWeek / 4.0;
    const overload =
      Math.max(0.0, weeklyEffectiveReps - this.config.recoveryOverloadThresholdEffectiveReps) /
      this.config.recoveryOverloadScale;
    const penalty = 1.0 / (1.0 + 0.22 * density + 0.35 * overload);
    return Math.max(0.5, Math.min(1.0, penalty * (0.75 + 0.3 * recovery)));
  }

  private timeResponse(weeks: number, noProgressiveOverload = true): number {
    if (weeks <= 0) return 0.0;
    const tau = noProgressiveOverload ? 13.0 : 20.0;
    let plateau = 1.0 - Math.exp(-weeks / tau);
    if (noProgressiveOverload && weeks > 12) {
      plateau *= 0.92 + 0.08 * Math.exp(-(weeks - 12) / 20);
    }
    return plateau;
  }

  public simulate(
    profile: Profile,
    workout: WorkoutItem[],
    weeks: number
  ): AdaptationResult {
    const deltas: Record<string, number> = emptyMuscles();
    const debug: Record<string, any> = {};

    if (weeks <= 0) {
      return {
        weeks,
        muscles: deltas as MuscleValues,
        body_fat_delta: 0.0,
      };
    }

    const rec = profile.recovery ?? 0.85;
    const adh = profile.adherence ?? 0.9;
    const expLevel = profile.experience ?? "beginner";
    const startingMuscles = profile.starting_muscles ?? {};

    for (const item of workout) {
      const ex = this.exerciseLookup[item.exercise_id];
      if (!ex) continue;

      const sets = item.sets ?? 1;
      const reps = item.reps ?? 10;
      const days = item.days_per_week ?? 3.0;
      const repsSession = item.reps_per_session !== undefined ? item.reps_per_session : sets * reps;

      const effort = this.effortFactor(item, profile);
      const weekly = repsSession * days * effort;
      const volume = this.volumeResponse(weekly);
      const recoveryVal = this.recoveryPenalty(days, weekly, rec);
      const timeVal = this.timeResponse(weeks, true);
      const levelVal = this.config.experienceResponse[expLevel] ?? 1.0;
      const effortQuality =
        this.config.effortQualityFloor +
        (1.0 - this.config.effortQualityFloor) * effort;

      const base =
        this.config.baseGrowthScale *
        levelVal *
        volume *
        effortQuality *
        recoveryVal *
        timeVal *
        adh;

      const per: Record<string, number> = {};
      const roles = [
        { role: "primary" as const, muscles: ex.primaryMuscles },
        { role: "secondary" as const, muscles: ex.secondaryMuscles },
        { role: "stabilizer" as const, muscles: ex.stabilizers },
      ];

      for (const { role, muscles } of roles) {
        for (const muscle of muscles) {
          if (muscle in deltas) {
            const starting = Math.max(0.0, Math.min(1.0, startingMuscles[muscle] ?? 0.0));
            const developmentHeadroom = 1.0 - 0.35 * starting;
            const coeff = this.config.roleCoefficients[role];
            const contribution = base * coeff * developmentHeadroom;
            deltas[muscle] = (deltas[muscle] || 0) + contribution;
            per[muscle] = (per[muscle] || 0) + contribution;
          }
        }
      }

      debug[item.exercise_id] = {
        weekly_effective_reps: weekly,
        effort,
        effort_quality: effortQuality,
        volume,
        recovery: recoveryVal,
        base,
        muscles: per,
      };
    }

    // Multi-exercise combination saturates
    const maxDelta = this.config.maxNormalizedMuscleDelta;
    const finalMuscles = emptyMuscles();
    for (const m of MUSCLES) {
      const v = deltas[m] || 0;
      finalMuscles[m] = Math.min(maxDelta, maxDelta * (1.0 - Math.exp(-v / maxDelta)));
    }

    return {
      weeks,
      muscles: finalMuscles,
      body_fat_delta: 0.0,
      debug,
    };
  }
}

export const defaultEngine = new MuscleAdaptationEngine();
