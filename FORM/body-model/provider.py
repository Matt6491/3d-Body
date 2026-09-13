
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict
from morphology import build_morph_controls

@dataclass
class BodyMeasurements:
    height_cm: float
    weight_kg: float
    shoulder_width_cm: float
    torso_length_cm: float
    chest_depth_cm: float
    waist_width_cm: float
    waist_depth_cm: float
    hip_width_cm: float
    arm_length_cm: float
    leg_length_cm: float
    upper_arm_proxy_cm: float
    forearm_proxy_cm: float
    thigh_proxy_cm: float
    calf_proxy_cm: float

@dataclass
class BodyState:
    measurements: BodyMeasurements
    muscles: Dict[str,float] = field(default_factory=dict)
    body_fat_parameter: float = 0.22
    source: str = "measurement-estimate"

class BodyModelProvider(ABC):
    @abstractmethod
    def createBodyFromMeasurements(self, measurements: BodyMeasurements) -> BodyState: ...
    @abstractmethod
    def fitBodyFromPhotos(self, analysis: dict, height_cm: float, weight_kg: float) -> BodyState: ...
    @abstractmethod
    def setMuscleParameter(self, body: BodyState, muscle: str, value: float) -> BodyState: ...
    @abstractmethod
    def setBodyCompositionParameter(self, body: BodyState, value: float) -> BodyState: ...
    @abstractmethod
    def getMesh(self, body: BodyState) -> dict: ...
    @abstractmethod
    def getTexture(self, body: BodyState) -> dict|None: ...
    @abstractmethod
    def renderBody(self, body: BodyState) -> dict: ...

class ParametricPrimitiveBodyProvider(BodyModelProvider):
    """License-safe prototype provider. Produces semantic dimensions consumed by R3F.

    This deliberately avoids pretending to be SMPL/SMPL-X. A licensed mesh provider can
    replace it without changing adaptation or UI APIs.
    """
    def createBodyFromMeasurements(self, measurements):
        return BodyState(measurements=measurements,muscles={})
    def fitBodyFromPhotos(self, analysis, height_cm, weight_kg):
        m=analysis["measurements"]
        return self.createBodyFromMeasurements(BodyMeasurements(height_cm=height_cm,weight_kg=weight_kg,**m))
    def setMuscleParameter(self, body, muscle, value):
        body.muscles[muscle]=float(value); return body
    def setBodyCompositionParameter(self, body, value):
        body.body_fat_parameter=float(value); return body
    def getMesh(self, body):
        return {"provider":"parametric-primitives","measurements":body.measurements.__dict__,"muscles":body.muscles,
                "morphControls":build_morph_controls(body.muscles),"bodyFat":body.body_fat_parameter}
    def getTexture(self, body): return None
    def renderBody(self, body): return self.getMesh(body)


def get_body_model_provider(name:str="parametric-primitives")->BodyModelProvider:
    if name=="parametric-primitives":
        return ParametricPrimitiveBodyProvider()
    if name in {"smpl","smpl-x","smplx"}:
        raise RuntimeError("SMPL-X provider is not bundled. Configure a separately licensed provider implementation before use.")
    raise ValueError(f"Unknown BodyModelProvider: {name}")
