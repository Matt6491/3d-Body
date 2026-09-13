import { NextRequest, NextResponse } from "next/server";
import { defaultEngine } from "@/lib/engine";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const weeks = Number(searchParams.get("weeks") || 12);

  const profile = {
    age: 35,
    sex: "male" as const,
    experience: "intermediate" as const,
    max_pushups: 25,
    recovery: 0.85,
    adherence: 0.95,
  };

  const item = {
    exercise_id: "pushup",
    sets: 5,
    reps: 20,
    days_per_week: 7,
    rir: 2,
  };

  const r = defaultEngine.simulate(profile, [item], weeks);
  const targeted = ["pectoralisMajor", "triceps", "anteriorDeltoid"] as const;
  const unrelated = [
    "quadriceps",
    "hamstrings",
    "calves",
    "glutes",
    "latissimus",
    "biceps",
  ] as const;

  const passed =
    targeted.every((x) => (r.muscles as any)[x] > 0) &&
    unrelated.every((x) => (r.muscles as any)[x] < 0.002) &&
    r.body_fat_delta === 0;

  return NextResponse.json({
    passed,
    targeted: Object.fromEntries(targeted.map((x) => [x, (r.muscles as any)[x]])),
    unrelated: Object.fromEntries(unrelated.map((x) => [x, (r.muscles as any)[x]])),
    bodyFatDelta: r.body_fat_delta,
  });
}
