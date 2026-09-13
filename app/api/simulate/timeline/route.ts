import { NextRequest, NextResponse } from "next/server";
import { defaultEngine } from "@/lib/engine";

const checkpoints = [0, 2, 4, 8, 12, 26, 39, 52];

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

    const states = checkpoints.map((weeks) => {
      const res = defaultEngine.simulate(profile, workout, weeks);
      return {
        weeks,
        muscles: res.muscles,
        bodyFatDelta: res.body_fat_delta,
      };
    });

    return NextResponse.json({ checkpoints: states });
  } catch (err: any) {
    return NextResponse.json(
      { error: err.message || "Timeline simulation failed" },
      { status: 400 }
    );
  }
}
