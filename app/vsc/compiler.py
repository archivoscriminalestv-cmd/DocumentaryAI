"""VisualSceneCompiler — ShotExecutionRequest + SceneVisualContext -> VisualGenerationRequest.

Compila un prompt POR CAPAS (GLOBAL -> ESCENA -> PLANO) en una descripción única y
coherente, manteniendo CONTINUIDAD: cámara, lente, clima, paleta e iluminación
provienen del ``SceneVisualContext`` (fuente de verdad de continuidad) y son
idénticas en todos los planos de la escena; el plano solo aporta variación
(sujeto, composición, lenguaje de cámara). Determinista, provider-agnóstico.
"""

import hashlib

from app.vsc.models import GlobalStyle, SceneVisualContext, VisualGenerationRequest

# camera_move (VAI) -> pista de movimiento para el futuro Motion Engine.
_MOTION_HINT = {
    "push_in": "slow_push_in",
    "pull_out": "slow_pull_out",
    "parallax": "parallax",
    "static": "locked",
    "tracking": "tracking_left",
    "drone": "aerial_descent",
    "orbital": "orbit",
    "ken_burns": "ken_burns_drift",
    "pan": "pan_right",
    "zoom_in": "slow_zoom",
}


def _dedupe(fragments: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for fragment in fragments:
        text = " ".join(str(fragment).split()).strip(" ,")
        if text and text.lower() not in seen:
            seen.add(text.lower())
            out.append(text)
    return out


def _seed(scene: SceneVisualContext, shot_id: str) -> int:
    if scene.seed_strategy == "per_shot" and shot_id:
        return scene.seed ^ int(hashlib.md5(shot_id.encode("utf-8")).hexdigest()[:8], 16)
    return scene.seed  # per_scene | fixed


class VisualSceneCompiler:
    def compile(
        self,
        shot_request,
        scene: SceneVisualContext,
        global_style: GlobalStyle | None = None,
    ) -> VisualGenerationRequest:
        gs = global_style or GlobalStyle()
        spec = getattr(shot_request, "specification", None)

        subject = getattr(spec, "subject", "") or "the subject"
        composition = list(getattr(spec, "composition", []) or [])
        camera_language = list(getattr(spec, "camera_language", []) or [])
        shot_negatives = list(getattr(spec, "negatives", []) or [])

        lead = camera_language[0] if camera_language else "cinematic shot"
        shot_style = ", ".join(_dedupe([lead, *camera_language[1:], *composition]))

        scene_style = ", ".join(_dedupe([
            scene.location,
            f"{scene.season} {scene.time_of_day}".strip(),
            scene.weather,
            scene.color_palette,
            f"shot on {scene.camera_package}",
            scene.lens_family,
            scene.lighting_language,
            scene.documentary_style,
        ]))
        global_style_text = ", ".join(_dedupe([gs.style, gs.realism, gs.quality]))

        # Prompt coherente por capas: PLANO (qué/cómo) -> ESCENA (continuidad) -> GLOBAL.
        prompt = ", ".join(_dedupe([
            f"{lead} of {subject}",
            *camera_language[1:],
            *composition,
            scene.location,
            f"{scene.season} {scene.time_of_day}".strip(),
            scene.weather,
            scene.color_palette,
            f"shot on {scene.camera_package}",
            scene.lens_family,
            scene.lighting_language,
            scene.documentary_style,
            gs.style, gs.realism, gs.quality,
        ]))

        negatives = ", ".join(_dedupe([*gs.base_negatives, *scene.negative_prompts, *shot_negatives]))

        motion = getattr(shot_request, "motion", {}) or {}
        motion_hint = _MOTION_HINT.get(str(motion.get("move", "")), "locked")

        shot_reuse = str(getattr(shot_request, "reuse_key", "") or "")
        reuse_key = "" if scene.reuse_policy == "off" else shot_reuse

        return VisualGenerationRequest(
            shot_id=str(getattr(shot_request, "shot_id", "")),
            scene_id=scene.scene_id,
            media_type=str(getattr(shot_request, "media_type", "image")),
            prompt=prompt,
            negative_prompt=negatives,
            global_style=global_style_text,
            scene_style=scene_style,
            shot_style=shot_style,
            camera=scene.camera_package,
            lens=scene.lens_family,
            lighting=scene.lighting_language,
            composition=composition[0] if composition else "",
            color=scene.color_palette,
            environment=", ".join(_dedupe([scene.location, scene.season, scene.time_of_day, scene.weather])),
            subject=subject,
            provider_constraints=dict(scene.provider_constraints),
            reuse_key=reuse_key,
            seed=_seed(scene, str(getattr(shot_request, "shot_id", ""))),
            seed_strategy=scene.seed_strategy,
            motion_hint=motion_hint,
        )

    def compile_scene(self, shot_requests: list, scene: SceneVisualContext, global_style: GlobalStyle | None = None) -> list[VisualGenerationRequest]:
        return [self.compile(req, scene, global_style) for req in shot_requests]
