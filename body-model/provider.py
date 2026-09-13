from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any
from .morphology import build_morph_controls

@dataclass
class BodyMeshState:
    provider: str
    measurements: Dict[str, float]
    muscles: Dict[str, float]
    morph_controls: Dict[str, Any]
    body_fat: float = 0.20

class BodyModelProvider(ABC):
    @abstractmethod
    def fit_baseline(self, measurements: Dict[str, float], body_fat: float = 0.20) -> BodyMeshState:
        pass

    @abstractmethod
    def apply_muscles(self, baseline: BodyMeshState, muscles: Dict[str, float], body_fat_delta: float = 0.0) -> BodyMeshState:
        pass

class ParametricPrimitiveBodyProvider(BodyModelProvider):
    def fit_baseline(self, measurements: Dict[str, float], body_fat: float = 0.20) -> BodyMeshState:
        return BodyMeshState(
            provider="parametric-primitives",
            measurements=measurements,
            muscles={},
            morph_controls=build_morph_controls({}),
            body_fat=body_fat,
        )

    def apply_muscles(self, baseline: BodyMeshState, muscles: Dict[str, float], body_fat_delta: float = 0.0) -> BodyMeshState:
        return BodyMeshState(
            provider="parametric-primitives",
            measurements=baseline.measurements,
            muscles=muscles,
            morph_controls=build_morph_controls(muscles),
            body_fat=baseline.body_fat + body_fat_delta,
        )
