"""VisualDirector — el Director de Fotografía de DocumentaryAI (orquestador VAI).

Coordina los motores especialistas para convertir un ``Shot`` de VIS en una
``VisualSpecification`` y, mediante el ``PromptOptimizer`` + ``NegativePromptEngine``,
en un ``ShotExecutionRequest`` listo para el MGL.

Reglas:
- NO modifica las decisiones de VIS (shot_type, camera_move, duración, ritmo,
  intención): las TRADUCE/ENRIQUECE. ``motion``/``media_type``/``reuse_key`` pasan tal cual.
- Independiente de proveedor: el request lleva prompt de texto universal + la
  ``specification`` estructurada.
- Determinista. Sin IA, sin red, sin APIs.

Los motores son inyectables (interfaz ``VisualEngine``): se pueden sustituir o
añadir sin tocar el director (desacoplamiento para crecer durante años).
"""

import hashlib

from app.vai.atmosphere_engine import AtmosphereEngine
from app.vai.camera_language_engine import CameraLanguageEngine
from app.vai.color_grading_engine import ColorGradingEngine
from app.vai.composition_engine import CompositionEngine
from app.vai.lens_engine import LensEngine
from app.vai.lighting_engine import LightingEngine
from app.vai.models import ShotExecutionRequest, VisualContext, VisualSpecification
from app.vai.negative_prompt_engine import NegativePromptEngine
from app.vai.prompt_optimizer import PromptOptimizer
from app.vai.quality_engine import QualityEngine
from app.vai.realism_engine import RealismEngine
from app.vai.visual_memory import VisualMemory

_ANGLE_BY_TYPE = {
    "impact": "low-angle", "aftermath": "high-angle", "establishing": "eye-level",
    "detail": "high-angle", "closeup": "eye-level", "action": "dynamic angle", "wide": "eye-level",
}


class VisualDirector:
    def __init__(
        self,
        *,
        composition=None, camera_language=None, lens=None, lighting=None,
        atmosphere=None, color_grade=None, realism=None, quality=None,
        negatives=None, optimizer=None, memory=None,
    ) -> None:
        self._composition = composition or CompositionEngine()
        self._camera_language = camera_language or CameraLanguageEngine()
        self._lens = lens or LensEngine()
        self._lighting = lighting or LightingEngine()
        self._atmosphere = atmosphere or AtmosphereEngine()
        self._color_grade = color_grade or ColorGradingEngine()
        self._realism = realism or RealismEngine()
        self._quality = quality or QualityEngine()
        self._negatives = negatives or NegativePromptEngine()
        self._optimizer = optimizer or PromptOptimizer()
        self._memory = memory or VisualMemory()

    @property
    def memory(self) -> VisualMemory:
        return self._memory

    def specify(self, shot, context: VisualContext) -> VisualSpecification:
        """Construye la VisualSpecification del plano (decisiones fotográficas)."""
        spec = VisualSpecification(
            shot_id=str(getattr(shot, "id", "")),
            scene_id=str(getattr(shot, "scene_id", "")),
            media_type=str(getattr(shot, "asset_type", "image")),
            subject=context.subject,
            style=context.style,
            composition=self._composition.contribute(shot, context),
            camera_language=self._camera_language.contribute(shot, context),
            lens=self._lens.contribute(shot, context),
            lighting=self._lighting.contribute(shot, context),
            atmosphere=self._atmosphere.contribute(shot, context),
            color_grade=self._color_grade.contribute(shot, context),
            realism=self._realism.contribute(shot, context),
            quality=self._quality.contribute(shot, context),
            negatives=self._negatives.contribute(shot, context),
        )
        return spec

    def direct(self, shot, context: VisualContext) -> ShotExecutionRequest:
        """Shot (VIS) -> ShotExecutionRequest (listo para el MGL)."""
        spec = self.specify(shot, context)
        prompt = self._optimizer.optimize(spec, context)
        shot_id = spec.shot_id

        request = ShotExecutionRequest(
            shot_id=shot_id,
            scene_id=spec.scene_id,
            media_type=spec.media_type,
            prompt=prompt,
            negative_prompt=", ".join(spec.negatives),
            reuse_key=str(getattr(shot, "reuse_key", "") or ""),
            variation_seed=int(hashlib.md5(shot_id.encode("utf-8")).hexdigest()[:8], 16) if shot_id else 0,
            motion={
                "move": getattr(shot, "camera_move", ""),
                "intensity": getattr(shot, "camera_intensity", 0.0),
            },
            lens=spec.lens[0] if spec.lens else "",
            angle=_ANGLE_BY_TYPE.get(str(getattr(shot, "shot_type", "")), "eye-level"),
            composition=spec.composition[0] if spec.composition else "",
            specification=spec,
        )
        self._memory.record(shot_id, spec)
        return request
