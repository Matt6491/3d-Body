export interface MorphRule {
  regions: string[];
  axisWeights: [number, number, number];
  surface: string;
  gain: number;
}

export const MORPH_RULES: Record<string, MorphRule> = {
  pectoralisMajor: {
    regions: ["chestLeft", "chestRight"],
    axisWeights: [0.45, 0.25, 1.0],
    surface: "anterior",
    gain: 1.0,
  },
  upperChest: {
    regions: ["upperChestLeft", "upperChestRight"],
    axisWeights: [0.4, 0.25, 0.85],
    surface: "anterior",
    gain: 0.8,
  },
  anteriorDeltoid: {
    regions: ["shoulderLeft", "shoulderRight"],
    axisWeights: [0.25, 0.35, 1.0],
    surface: "anterior",
    gain: 0.75,
  },
  lateralDeltoid: {
    regions: ["shoulderLeft", "shoulderRight"],
    axisWeights: [1.0, 0.45, 0.25],
    surface: "lateral",
    gain: 0.9,
  },
  posteriorDeltoid: {
    regions: ["shoulderLeft", "shoulderRight"],
    axisWeights: [0.25, 0.35, 1.0],
    surface: "posterior",
    gain: 0.75,
  },
  triceps: {
    regions: ["upperArmLeft", "upperArmRight"],
    axisWeights: [0.35, 0.55, 1.0],
    surface: "posterior",
    gain: 0.9,
  },
  biceps: {
    regions: ["upperArmLeft", "upperArmRight"],
    axisWeights: [0.35, 0.55, 1.0],
    surface: "anterior",
    gain: 0.9,
  },
  forearms: {
    regions: ["forearmLeft", "forearmRight"],
    axisWeights: [0.6, 0.4, 0.6],
    surface: "circumferential",
    gain: 0.62,
  },
  trapezius: {
    regions: ["trapezius"],
    axisWeights: [0.55, 0.55, 0.75],
    surface: "posterior-superior",
    gain: 0.65,
  },
  latissimus: {
    regions: ["latLeft", "latRight"],
    axisWeights: [1.0, 0.35, 0.45],
    surface: "posterior-lateral",
    gain: 0.88,
  },
  upperBack: {
    regions: ["upperBack"],
    axisWeights: [0.65, 0.35, 0.8],
    surface: "posterior",
    gain: 0.7,
  },
  abdominals: {
    regions: ["abdominalWall"],
    axisWeights: [0.2, 0.45, 1.0],
    surface: "anterior",
    gain: 0.55,
  },
  obliques: {
    regions: ["obliqueLeft", "obliqueRight"],
    axisWeights: [0.8, 0.4, 0.25],
    surface: "lateral",
    gain: 0.52,
  },
  glutes: {
    regions: ["gluteLeft", "gluteRight"],
    axisWeights: [0.45, 0.45, 1.0],
    surface: "posterior",
    gain: 0.95,
  },
  quadriceps: {
    regions: ["thighLeft", "thighRight"],
    axisWeights: [0.4, 0.55, 1.0],
    surface: "anterior",
    gain: 0.9,
  },
  hamstrings: {
    regions: ["thighLeft", "thighRight"],
    axisWeights: [0.4, 0.55, 1.0],
    surface: "posterior",
    gain: 0.82,
  },
  calves: {
    regions: ["calfLeft", "calfRight"],
    axisWeights: [0.55, 0.55, 0.75],
    surface: "posterior-lateral",
    gain: 0.72,
  },
};

export function buildMorphControls(muscles: Record<string, number>): Record<string, any[]> {
  const out: Record<string, any[]> = {};
  for (const [muscle, value] of Object.entries(muscles)) {
    if (!value || value <= 0 || !MORPH_RULES[muscle]) continue;
    const rule = MORPH_RULES[muscle];
    const amount = value * rule.gain;
    out[muscle] = rule.regions.map((region) => ({
      region,
      surface: rule.surface,
      scaleDelta: rule.axisWeights.map((w) => Number((amount * w).toFixed(6))),
    }));
  }
  return out;
}
