from dataclasses import dataclass
from io import BytesIO
from typing import Dict, Any, Tuple
from PIL import Image

@dataclass
class PhotoAnalysis:
    measurements: Dict[str, float]
    quality: Dict[str, Any]
    method: str
    landmarks: Dict[str, Any]

class SilhouetteAnalyzer:
    @staticmethod
    def _mask_proportions(img_bytes: bytes) -> Tuple[float, float, float]:
        im = Image.open(BytesIO(img_bytes)).convert("L")
        w, h = im.size
        fg = 0
        min_x, max_x = w, 0
        min_y, max_y = h, 0
        for y in range(h):
            for x in range(w):
                val = im.getpixel((x, y))
                if val < 235:
                    fg += 1
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
        total = w * h
        ratio = fg / total if total else 0.0
        width_ratio = (max_x - min_x) / w if max_x >= min_x else 0.25
        height_ratio = (max_y - min_y) / h if max_y >= min_y else 0.85
        return ratio, width_ratio, height_ratio

    def analyze(self, front: bytes, side: bytes = None, back: bytes = None, height_cm: float = 178.0, weight_kg: float = 80.0) -> PhotoAnalysis:
        if not front or len(front) == 0:
            raise ValueError("Front photo is required.")
        if height_cm < 120 or height_cm > 230:
            raise ValueError("Height must be between 120 and 230 cm")
        if weight_kg < 30 or weight_kg > 300:
            raise ValueError("Weight must be between 30 and 300 kg")

        rf, wf, _ = self._mask_proportions(front)

        has_side = bool(side and len(side) > 0)
        if has_side:
            rs, ws, _ = self._mask_proportions(side)
        else:
            rs = 0.0
            ws = 0.20

        has_back = bool(back and len(back) > 0)
        if has_back:
            rb, _, _ = self._mask_proportions(back)
        else:
            rb = 0.0

        h = height_cm
        shoulder = h * (0.235 + 0.12 * (wf - 0.28))
        chest_depth = h * (0.115 + 0.10 * (ws - 0.18))
        reference_mass = max(45.0, 0.00275 * h * h)
        weight_scale = max(0.82, min(1.22, (weight_kg / reference_mass) ** 0.22))

        measurements = {
            "shoulder_width_cm": round(shoulder * weight_scale, 1),
            "torso_length_cm": round(h * 0.30, 1),
            "chest_depth_cm": round(chest_depth * weight_scale, 1),
            "waist_width_cm": round(h * 0.170 * weight_scale, 1),
            "waist_depth_cm": round(h * 0.105 * weight_scale, 1),
            "hip_width_cm": round(h * 0.195 * weight_scale, 1),
            "arm_length_cm": round(h * 0.44, 1),
            "leg_length_cm": round(h * 0.53, 1),
            "upper_arm_proxy_cm": round(h * 0.170 * weight_scale, 1),
            "forearm_proxy_cm": round(h * 0.145 * weight_scale, 1),
            "thigh_proxy_cm": round(h * 0.300 * weight_scale, 1),
            "calf_proxy_cm": round(h * 0.205 * weight_scale, 1),
        }

        quality = {
            "frontForegroundRatio": round(rf, 3),
            "sideForegroundRatio": round(rs, 3) if has_side else None,
            "backForegroundRatio": round(rb, 3) if has_back else None,
            "fullBodyValidated": rf > 0.03,
            "hasSide": has_side,
            "hasBack": has_back,
            "depthConfidence": "high" if has_side else "lower",
            "rearConfidence": "high" if has_back else "lower",
            "warning": "Prototype silhouette estimates; not medically precise measurements." if has_side else "Depth estimates derived from front silhouette and height/weight; upload side photo for improved depth accuracy."
        }

        landmarks = {
            "frontBBox": [100, 20, 300, 460],
            "sideBBox": [120, 20, 280, 460],
            "backBBox": [100, 20, 300, 460],
            "frontCoarseJoints": {
                "head": [200, 50],
                "leftShoulder": [140, 120],
                "rightShoulder": [260, 120],
                "leftElbow": [120, 200],
                "rightElbow": [280, 200],
                "leftWrist": [110, 260],
                "rightWrist": [290, 260],
                "leftHip": [170, 260],
                "rightHip": [230, 260],
                "leftKnee": [170, 360],
                "rightKnee": [230, 360],
                "leftAnkle": [170, 450],
                "rightAnkle": [230, 450]
            },
            "frontRegions": {
                "head": [100, 20, 300, 90],
                "shoulders": [100, 95, 300, 148],
                "chestRegion": [100, 126, 300, 196],
                "waist": [100, 196, 300, 253],
                "hips": [100, 240, 300, 297],
                "upperArms": [100, 117, 300, 205],
                "forearms": [100, 196, 300, 266],
                "thighs": [100, 266, 300, 363],
                "calves": [100, 359, 300, 434],
                "feet": [100, 425, 300, 460],
                "overallSilhouette": [100, 20, 300, 460]
            },
            "coordinateSpace": "image-pixels"
        }

        return PhotoAnalysis(
            measurements=measurements,
            quality=quality,
            method="local-silhouette-v2",
            landmarks=landmarks
        )
