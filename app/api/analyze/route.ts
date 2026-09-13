import { NextRequest, NextResponse } from "next/server";
import { analyzer } from "@/lib/silhouette";
import { buildMorphControls } from "@/lib/morphology";
import { repo } from "@/lib/storage";

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const consent = formData.get("consent") === "true";
    const adultConfirmed = formData.get("adult_confirmed") === "true";
    const age = Number(formData.get("age") || 35);
    const sex = String(formData.get("sex") || "male");
    const heightCm = Number(formData.get("height_cm") || 178);
    const weightKg = Number(formData.get("weight_kg") || 80);
    const experience = String(formData.get("experience") || "beginner");
    const autoDelete = formData.get("auto_delete_originals") === "true";
    const excludeFace = formData.get("exclude_face") === "true";

    const bodyFatEstimate = formData.get("body_fat_estimate")
      ? Number(formData.get("body_fat_estimate"))
      : null;
    const trainingFrequency = formData.get("training_frequency")
      ? Number(formData.get("training_frequency"))
      : null;

    const knownShoulder = formData.get("known_shoulder_width_cm")
      ? Number(formData.get("known_shoulder_width_cm"))
      : null;
    const knownWaist = formData.get("known_waist_width_cm")
      ? Number(formData.get("known_waist_width_cm"))
      : null;
    const knownHip = formData.get("known_hip_width_cm")
      ? Number(formData.get("known_hip_width_cm"))
      : null;

    if (!consent) {
      return NextResponse.json(
        { detail: "Explicit photo-processing consent is required." },
        { status: 400 }
      );
    }
    if (!adultConfirmed || age < 18) {
      return NextResponse.json(
        { detail: "FORM accepts adults age 18 or older only." },
        { status: 400 }
      );
    }

    const frontFile = formData.get("front") as File | null;
    const sideFile = formData.get("side") as File | null;
    const backFile = formData.get("back") as File | null;

    if (!frontFile || (frontFile instanceof File && frontFile.size === 0)) {
      return NextResponse.json(
        { detail: "Front photo is required." },
        { status: 400 }
      );
    }

    const frontBuffer = await frontFile.arrayBuffer();
    const sideBuffer =
      sideFile && sideFile instanceof File && sideFile.size > 0
        ? await sideFile.arrayBuffer()
        : null;
    const backBuffer =
      backFile && backFile instanceof File && backFile.size > 0
        ? await backFile.arrayBuffer()
        : null;

    const result = analyzer.analyze(frontBuffer, sideBuffer, backBuffer, heightCm, weightKg);

    if (knownShoulder !== null) result.measurements.shoulder_width_cm = knownShoulder;
    if (knownWaist !== null) result.measurements.waist_width_cm = knownWaist;
    if (knownHip !== null) result.measurements.hip_width_cm = knownHip;

    const bodyFatParam = bodyFatEstimate !== null ? bodyFatEstimate / 100 : 0.22;
    const bodyMesh = {
      provider: "parametric-primitives",
      measurements: {
        height_cm: heightCm,
        weight_kg: weightKg,
        ...result.measurements,
      },
      muscles: {},
      morphControls: buildMorphControls({}),
      bodyFat: bodyFatParam,
    };

    const aid = repo.saveAnalysis(null, result);
    const bid = repo.saveBody(null, bodyMesh, {
      age,
      sex,
      experience,
      trainingFrequency,
      selfReportedBodyFat: bodyFatEstimate,
    });

    return NextResponse.json({
      analysisId: aid,
      bodyId: bid,
      analysis: result,
      body: bodyMesh,
      originalPhotosRetained: false,
      faceAppearanceRetained: false,
      privacy: {
        requestedAutoDelete: autoDelete,
        excludeFace,
        localModeAlwaysDiscardsOriginals: true,
      },
    });
  } catch (err: any) {
    return NextResponse.json(
      { detail: err.message || "Photo analysis failed" },
      { status: 422 }
    );
  }
}
