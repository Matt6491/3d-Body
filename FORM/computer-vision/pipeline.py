
from __future__ import annotations
from dataclasses import dataclass
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import numpy as np

@dataclass
class PhotoAnalysis:
    measurements: dict
    quality: dict
    method: str
    landmarks: dict

class SilhouetteAnalyzer:
    """Local deterministic CV fallback for neutral full-body captures.

    This is intentionally not branded as medical measurement or full 3D reconstruction.
    It extracts foreground silhouettes, coarse neutral-pose joints, and scale-normalized
    body-proportion proxies. A production pose/segmentation implementation can replace
    this class behind the same return contract.
    """
    MIN_PIXELS = 240 * 480
    MAX_PIXELS = 16_000_000

    def _mask(self, data: bytes):
        try:
            raw=Image.open(BytesIO(data))
            w,h=raw.size
            if w*h < self.MIN_PIXELS:
                raise ValueError("Image resolution is too low for full-body analysis")
            if w*h > self.MAX_PIXELS:
                raise ValueError("Image resolution is too large; resize below 16 megapixels")
            im=raw.convert("RGB")
        except UnidentifiedImageError as e:
            raise ValueError("Unsupported or corrupt image") from e
        arr=np.asarray(im).astype(np.float32)
        # Background color estimate from all four borders.
        border=np.concatenate([arr[0],arr[-1],arr[:,0],arr[:,-1]],axis=0)
        bg=np.median(border,axis=0)
        dist=np.linalg.norm(arr-bg,axis=2)
        # Absolute floor prevents a blank image from creating a false silhouette.
        p75=float(np.percentile(dist,75))
        thresh=max(18.0,min(70.0,p75*0.72))
        mask=dist>thresh

        # Cheap neighborhood majority cleanup, no scipy/OpenCV dependency.
        padded=np.pad(mask.astype(np.uint8),1)
        acc=np.zeros_like(mask,dtype=np.uint8)
        for dy in range(3):
            for dx in range(3):
                acc += padded[dy:dy+h,dx:dx+w]
        mask=acc>=4
        ys,xs=np.where(mask)
        ratio=len(xs)/(h*w)
        if ratio<0.025:
            raise ValueError("Could not isolate a full-body silhouette; use a plain contrasting background")
        if ratio>0.72:
            raise ValueError("Foreground covers too much of the frame; step farther from the camera")
        bbox=(int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()))
        bw=bbox[2]-bbox[0]+1; bh=bbox[3]-bbox[1]+1
        if bh/h<0.62:
            raise ValueError("Full body is not visible from head to feet")
        if bbox[1] <= 1 or bbox[3] >= h-2:
            # Touching top/bottom strongly suggests clipped anatomy.
            raise ValueError("Leave visible space above the head and below the feet")
        return mask,bbox,(w,h)

    @staticmethod
    def _row_span(mask: np.ndarray, y:int):
        y=max(0,min(mask.shape[0]-1,int(y)))
        xs=np.where(mask[y])[0]
        if len(xs)<2:return None
        return int(xs.min()),int(xs.max())

    def _coarse_joints(self, mask:np.ndarray, bbox:tuple[int,int,int,int]):
        """Estimate neutral-pose landmarks from silhouette bands.

        These are geometric anchors, not pose-estimation confidence claims.
        """
        x0,y0,x1,y1=bbox
        bh=y1-y0; cx=(x0+x1)/2
        levels={"shoulder":.22,"elbow":.39,"wrist":.53,"hip":.53,"knee":.75,"ankle":.94}
        out={"head":[round(cx,1),round(y0+bh*.07,1)]}
        for name,rel in levels.items():
            y=y0+bh*rel
            span=self._row_span(mask,int(y))
            if span:
                lx,rx=span
                if name in ("shoulder","elbow","wrist"):
                    out[f"left{name.capitalize()}"]=[float(lx),round(y,1)]
                    out[f"right{name.capitalize()}"]=[float(rx),round(y,1)]
                else:
                    quarter=(rx-lx)*.25
                    out[f"left{name.capitalize()}"]=[round(cx-quarter,1),round(y,1)]
                    out[f"right{name.capitalize()}"]=[round(cx+quarter,1),round(y,1)]
        return out


    @staticmethod
    def _region_bands(bbox:tuple[int,int,int,int]):
        x0,y0,x1,y1=bbox; bh=y1-y0
        def band(a,b):
            return [int(x0),int(y0+bh*a),int(x1),int(y0+bh*b)]
        return {
          "head":band(0.00,0.16),
          "shoulders":band(0.17,0.29),
          "chestRegion":band(0.24,0.40),
          "waist":band(0.40,0.53),
          "hips":band(0.50,0.63),
          "upperArms":band(0.22,0.42),
          "forearms":band(0.40,0.56),
          "thighs":band(0.56,0.78),
          "calves":band(0.77,0.94),
          "feet":band(0.92,1.00),
          "overallSilhouette":[int(x0),int(y0),int(x1),int(y1)]
        }

    def analyze(self, front:bytes, side:bytes, back:bytes, height_cm:float, weight_kg:float) -> PhotoAnalysis:
        if not (120 <= height_cm <= 230):
            raise ValueError("Height must be between 120 and 230 cm")
        if not (30 <= weight_kg <= 300):
            raise ValueError("Weight must be between 30 and 300 kg")
        fm,fb,fs=self._mask(front); sm,sb,ss=self._mask(side); bm,bb,bs=self._mask(back)

        front_width=(fb[2]-fb[0]+1)/fs[0]
        side_width=(sb[2]-sb[0]+1)/ss[0]
        h=height_cm

        # Heuristic anthropometric priors, perturbed by observed neutral-pose silhouette.
        # These are intentionally labeled proxies and must be validated against a measured cohort.
        shoulder=h*(0.235 + 0.12*(front_width-0.28))
        chest_depth=h*(0.115 + 0.10*(side_width-0.18))
        reference_mass=max(45,0.00275*h*h)
        weight_scale=max(.82,min(1.22,(weight_kg/reference_mass)**0.22))
        vals={
          "shoulder_width_cm":round(shoulder*weight_scale,1),
          "torso_length_cm":round(h*0.30,1),
          "chest_depth_cm":round(chest_depth*weight_scale,1),
          "waist_width_cm":round(h*0.17*weight_scale,1),
          "waist_depth_cm":round(h*0.105*weight_scale,1),
          "hip_width_cm":round(h*0.195*weight_scale,1),
          "arm_length_cm":round(h*0.44,1),
          "leg_length_cm":round(h*0.53,1),
          "upper_arm_proxy_cm":round(h*0.17*weight_scale,1),
          "forearm_proxy_cm":round(h*0.145*weight_scale,1),
          "thigh_proxy_cm":round(h*0.30*weight_scale,1),
          "calf_proxy_cm":round(h*0.205*weight_scale,1),
        }
        quality={
          "frontForegroundRatio":round(float(fm.mean()),4),
          "sideForegroundRatio":round(float(sm.mean()),4),
          "backForegroundRatio":round(float(bm.mean()),4),
          "fullBodyValidated":True,
          "warning":"Prototype silhouette estimates; not medically precise measurements."
        }
        landmarks={
          "frontBBox":[int(x) for x in fb],
          "sideBBox":[int(x) for x in sb],
          "backBBox":[int(x) for x in bb],
          "frontCoarseJoints":self._coarse_joints(fm,fb),
          "frontRegions":self._region_bands(fb),
          "coordinateSpace":"image-pixels"
        }
        return PhotoAnalysis(vals,quality,"local-silhouette-v2",landmarks)

class MediaPipeAnalyzer:
    """Optional production-oriented adapter placeholder.

    Keep MediaPipe behind this interface so a commercially suitable or internally trained
    model can replace it without changing backend routes or body fitting code.
    """
    def __init__(self):
        try:
            import mediapipe as mp  # type: ignore
        except ImportError as e:
            raise RuntimeError("mediapipe is not installed in this environment") from e
        self.mp=mp
        raise RuntimeError("MediaPipe adapter is intentionally not activated until landmark/segmentation model assets and license review are pinned.")
