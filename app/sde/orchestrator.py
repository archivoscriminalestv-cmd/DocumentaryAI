"""ShotDiversityEngine — fachada del SDE (VAI → SDE → VSC).

Recibe un ``ShotExecutionRequest`` del VAI + un ``SDEContext`` (datos de escena ya
disponibles) y devuelve OTRO ``ShotExecutionRequest`` con la composición enriquecida.
Solo modifica campos estructurados (``specification.camera_language`` /
``specification.composition`` y los representativos ``lens``/``angle``/``composition``);
nunca toca subject, prompt-completo, identidad, escena ni el VPL.
"""

import dataclasses
import logging
from dataclasses import dataclass

from app.sde.continuity import assert_identity_preserved
from app.sde.history import ShotHistory
from app.sde.models import VARIABLE_DIMENSIONS, ShotRecord
from app.sde.planner import DiversityPlanner
from app.sde.rules import classify_narrative, parse_base_fingerprint, render_to_spec
from app.sde.scoring import average_diversity

# 'orbit' (vocabulario SDE) -> 'orbital' (clave que entiende el VSC para motion_hint).
_MOTION_ALIAS = {"orbit": "orbital"}


@dataclass
class SDEContext:
    scene_id: str = ""
    documentary_style: str = ""
    location: str = ""
    color_palette: str = ""
    time_of_day: str = ""
    weather: str = ""
    lighting: str = ""
    character_name: str = ""
    identity: str = ""
    shot_role: str = ""


class ShotDiversityEngine:
    def __init__(self, history: ShotHistory | None = None, *, logger=None) -> None:
        self.history = history or ShotHistory()
        self._planner = DiversityPlanner()
        self._log = logger or logging.getLogger("sde")

    def process(self, request, ctx: SDEContext):
        spec = getattr(request, "specification", None)
        if spec is None:
            return request  # nada que diversificar de forma estructurada

        base_fp = parse_base_fingerprint(request, ctx)
        mode = classify_narrative(ctx.documentary_style, ctx.shot_role)
        final_fp, changes, score = self._planner.plan(base_fp, mode, self.history)
        assert_identity_preserved(base_fp, final_fp)  # red de seguridad

        camera_language, composition = render_to_spec(final_fp)
        new_spec = dataclasses.replace(spec, camera_language=camera_language, composition=composition)

        motion = dict(getattr(request, "motion", {}) or {})
        motion["move"] = _MOTION_ALIAS.get(final_fp.movement, final_fp.movement)

        new_request = dataclasses.replace(
            request, specification=new_spec, motion=motion,
            lens=f"{final_fp.lens}mm lens", angle=final_fp.camera_angle,
            composition=composition[0],
        )

        self.history.append(ShotRecord(
            index=len(self.history), shot_id=str(getattr(request, "shot_id", "")),
            scene=ctx.scene_id, narrative_mode=mode,
            fingerprint=final_fp, base_fingerprint=base_fp,
            diversity_score=score, changes=changes,
        ))
        if changes:
            self._log.info("SDE shot=%s mode=%s diversity=%.2f changes=%d",
                           getattr(request, "shot_id", "?"), mode, score, len(changes))
        return new_request

    # ------------------------------------------------------------------ informe

    def average_diversity(self, window: int = 6) -> float:
        return average_diversity([r.fingerprint for r in self.history.all()], window)

    def stats(self) -> dict:
        records = self.history.all()
        repeats = sum(1 for r in records if r.diversity_score < 0.5)
        variations = sum(len(r.changes) for r in records)
        return {
            "total_shots": len(records),
            "average_diversity": self.average_diversity(),
            "repetitions_detected": repeats,
            "variations_applied": variations,
            "by_shot_size": self.history.distribution("shot_size"),
            "by_lens": self.history.distribution("lens"),
            "by_composition": self.history.distribution("composition"),
            "by_angle": self.history.distribution("camera_angle"),
            "by_height": self.history.distribution("camera_height"),
        }
