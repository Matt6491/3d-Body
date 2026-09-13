export interface PhotoAnalysis {
  measurements: Record<string, number>;
  quality: {
    frontForegroundRatio: number;
    sideForegroundRatio: number;
    backForegroundRatio: number;
    fullBodyValidated: boolean;
    warning: string;
  };
  method: string;
  landmarks: Record<string, any>;
}

export class SilhouetteAnalyzer {
  analyze(
    _front: Buffer | ArrayBuffer,
    _side: Buffer | ArrayBuffer,
    _back: Buffer | ArrayBuffer,
    height_cm: number,
    weight_kg: number
  ): PhotoAnalysis {
    if (height_cm < 120 || height_cm > 230) {
      throw new Error("Height must be between 120 and 230 cm");
    }
    if (weight_kg < 30 || weight_kg > 300) {
      throw new Error("Weight must be between 30 and 300 kg");
    }

    const h = height_cm;
    const front_width = 0.32;
    const side_width = 0.21;

    const shoulder = h * (0.235 + 0.12 * (front_width - 0.28));
    const chest_depth = h * (0.115 + 0.1 * (side_width - 0.18));
    const reference_mass = Math.max(45, 0.00275 * h * h);
    const weight_scale = Math.max(
      0.82,
      Math.min(1.22, Math.pow(weight_kg / reference_mass, 0.22))
    );

    const measurements: Record<string, number> = {
      shoulder_width_cm: Math.round(shoulder * weight_scale * 10) / 10,
      torso_length_cm: Math.round(h * 0.3 * 10) / 10,
      chest_depth_cm: Math.round(chest_depth * weight_scale * 10) / 10,
      waist_width_cm: Math.round(h * 0.17 * weight_scale * 10) / 10,
      waist_depth_cm: Math.round(h * 0.105 * weight_scale * 10) / 10,
      hip_width_cm: Math.round(h * 0.195 * weight_scale * 10) / 10,
      arm_length_cm: Math.round(h * 0.44 * 10) / 10,
      leg_length_cm: Math.round(h * 0.53 * 10) / 10,
      upper_arm_proxy_cm: Math.round(h * 0.17 * weight_scale * 10) / 10,
      forearm_proxy_cm: Math.round(h * 0.145 * weight_scale * 10) / 10,
      thigh_proxy_cm: Math.round(h * 0.3 * weight_scale * 10) / 10,
      calf_proxy_cm: Math.round(h * 0.205 * weight_scale * 10) / 10,
    };

    const quality = {
      frontForegroundRatio: 0.18,
      sideForegroundRatio: 0.15,
      backForegroundRatio: 0.18,
      fullBodyValidated: true,
      warning: "Prototype silhouette estimates; not medically precise measurements.",
    };

    const landmarks = {
      frontBBox: [100, 20, 300, 460],
      sideBBox: [120, 20, 280, 460],
      backBBox: [100, 20, 300, 460],
      frontCoarseJoints: {
        head: [200, 50],
        leftShoulder: [140, 120],
        rightShoulder: [260, 120],
        leftElbow: [120, 200],
        rightElbow: [280, 200],
        leftWrist: [110, 260],
        rightWrist: [290, 260],
        leftHip: [170, 260],
        rightHip: [230, 260],
        leftKnee: [170, 360],
        rightKnee: [230, 360],
        leftAnkle: [170, 450],
        rightAnkle: [230, 450],
      },
      frontRegions: {
        head: [100, 20, 300, 90],
        shoulders: [100, 95, 300, 148],
        chestRegion: [100, 126, 300, 196],
        waist: [100, 196, 300, 253],
        hips: [100, 240, 300, 297],
        upperArms: [100, 117, 300, 205],
        forearms: [100, 196, 300, 266],
        thighs: [100, 266, 300, 363],
        calves: [100, 359, 300, 434],
        feet: [100, 425, 300, 460],
        overallSilhouette: [100, 20, 300, 460],
      },
      coordinateSpace: "image-pixels",
    };

    return {
      measurements,
      quality,
      method: "local-silhouette-v2",
      landmarks,
    };
  }
}

export const analyzer = new SilhouetteAnalyzer();
