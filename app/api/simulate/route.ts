import { NextRequest, NextResponse } from "next/server";
import { defaultEngine } from "@/lib/engine";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const {
      age = 35,
      sex = "male",
      experience = "beginner",
      recovery = 0.85,
      adherence = 0.9,
      maxPushups = 25,
      startingMuscles = {},
      weeks = 12,
      workout = [],
    } = body;

    const profile = {
      age,
      sex,
      experience,
      recovery,
      adherence,
      max_pushups: maxPushups,
      starting_muscles: startingMuscles,
    };

    const res = defaultEngine.simulate(profile, workout, weeks);
    return NextResponse.json({
      weeks: res.weeks,
      muscles: res.muscles,
      bodyFatDelta: res.body_fat_delta,
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: err.message || "Simulation failed" },
      { status: 400 }
    );
  }
}
