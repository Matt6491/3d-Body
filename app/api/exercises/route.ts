import { NextResponse } from "next/server";
import exercisesData from "@/data/exercises.json";

export async function GET() {
  return NextResponse.json(exercisesData);
}
