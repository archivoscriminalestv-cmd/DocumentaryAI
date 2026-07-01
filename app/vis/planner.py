"""VIS-1 (real, mínimo): CinematicProfile (RDA) + Scene -> VisualPlan.

Las métricas del RDA CAMBIAN decisiones de forma visible y determinista:
- avg_shot_length + duración de escena -> nº de planos,
- movement_tendency -> repertorio e intensidad de cámara,
- lighting_tendency -> iluminación,
- color_temperature/saturation -> grade,
- pacing_tier/variety -> duraciones.
Sin LLM, sin red.
"""

from app.vis.models import PlannedShot, VisualPlan

_SECONDS_PER_WORD = 0.4
_MIN_SCENE_SECONDS = 3.0

_MOVE_POOL = {
    "dynamic": ["tracking", "push_in", "drone", "orbital"],
    "moderate": ["push_in", "parallax", "pan", "ken_burns"],
    "mostly_static": ["ken_burns", "parallax", "push_in"],
}
_MOVE_INTENSITY = {"dynamic": 0.75, "moderate": 0.5, "mostly_static": 0.35}

# Secuencia base de tipos de plano (contexto -> detalle -> acción -> clímax -> cierre).
_BODY_CYCLE = ["wide", "detail", "action", "closeup"]
_SHOT_FACTOR = {
    "establishing": 1.3, "wide": 1.1, "detail": 0.7, "closeup": 0.75,
    "action": 1.0, "impact": 1.3, "aftermath": 1.1,
}
_VARIETY_JITTER = {"metronomic": 0.05, "moderate": 0.20, "varied": 0.40}

# Vocabulario de movimiento del conocimiento (KBG/DLE) -> tendencia que entiende VIS.
# Solo se aplica si el valor está mapeado; si no, no se sobreescribe nada.
_MOVEMENT_MAP = {
    "static": "mostly_static", "mostly_static": "mostly_static", "subtle": "mostly_static",
    "slow": "mostly_static", "pan": "moderate", "tilt": "moderate", "zoom": "moderate",
    "moderate": "moderate", "push_in": "moderate", "tracking": "dynamic",
    "handheld": "dynamic", "dynamic": "dynamic", "fast": "dynamic",
}


def _estimate_scene_duration(scene) -> float:
    words = len(str(getattr(scene, "narration", "")).split())
    return max(_MIN_SCENE_SECONDS, words * _SECONDS_PER_WORD)


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _shot_sequence(n: int) -> list[str]:
    seq = ["establishing"]
    while len(seq) < n - 1:
        seq.append(_BODY_CYCLE[(len(seq) - 1) % len(_BODY_CYCLE)])
    if n >= 3:
        seq[-1] = "impact"        # clímax hacia el final
    seq.append("aftermath")       # cierre
    return seq[:n]


def _lighting(tendency: str) -> str:
    t = (tendency or "").lower()
    if t.startswith("low-key"):
        return "low-key chiaroscuro, hard rim light"
    if t.startswith("high-key"):
        return "high-key, soft fill, bright"
    return "soft natural light"


def _grade(temperature: str, saturation: str) -> str:
    return f"{temperature} {saturation} color grade".strip()


def build_visual_plan(
    profile,
    scene,
    *,
    style: str = "documentary",
    scene_duration: float | None = None,
    min_shots: int = 5,
    max_shots: int = 8,
    context=None,
) -> VisualPlan:
    """``context`` (opcional): un ``ProductionContext`` (PCX). Si se provee, sus decisiones
    CONOCIDAS tienen prioridad sobre las del RDA; las UNKNOWN (ausentes) se ignoran por
    completo y VIS se comporta exactamente igual que antes. VIS solo conoce este contrato;
    nunca KBG/knowledge/DLE/DKS/etc."""
    # Valores base derivados del RDA (comportamiento previo intacto).
    asl = _clamp(float(getattr(profile, "avg_shot_length", 3.0) or 3.0), 1.5, 8.0)
    movement = str(getattr(profile, "movement_tendency", "moderate"))
    lighting_src = str(getattr(profile, "lighting_tendency", "balanced"))
    plan_lighting = str(getattr(profile, "lighting_tendency", ""))
    temperature = str(getattr(profile, "color_temperature", "neutral"))
    saturation = str(getattr(profile, "saturation_tendency", "moderate"))
    pacing_tier = str(getattr(profile, "pacing_tier", ""))

    # ProductionContext: el conocimiento aprendido manda SOLO cuando existe y es conocido.
    if context is not None:
        asd = context.get("storytelling", "average_shot_duration")
        if isinstance(asd, (int, float)) and asd > 0:
            asl = _clamp(float(asd), 1.5, 8.0)
        mapped = _MOVEMENT_MAP.get(str(context.get("cinematography", "dominant_movement")).lower())
        if mapped:
            movement = mapped
        lighting_ctx = context.get("cinematography", "lighting")
        if lighting_ctx:
            lighting_src = plan_lighting = str(lighting_ctx)
        temperature_ctx = context.get("cinematography", "color_temperature")
        if temperature_ctx:
            temperature = str(temperature_ctx)
        pacing_ctx = context.get("storytelling", "pacing")
        if pacing_ctx:
            pacing_tier = str(pacing_ctx)

    duration = scene_duration or _estimate_scene_duration(scene)
    n = int(_clamp(round(duration / asl), min_shots, max_shots))

    moves = _MOVE_POOL.get(movement, _MOVE_POOL["moderate"])
    base_intensity = _MOVE_INTENSITY.get(movement, 0.5)
    lighting = _lighting(lighting_src)
    grade = _grade(temperature, saturation)
    variety = str(getattr(profile, "shot_length_variety", "moderate"))
    jitter = _VARIETY_JITTER.get(variety, 0.20)

    scene_id = str(getattr(scene, "id", "scene"))
    fact_ids = list(getattr(scene, "fact_ids", []) or [])
    seq = _shot_sequence(n)

    shots: list[PlannedShot] = []
    for i, shot_type in enumerate(seq):
        move = moves[i % len(moves)]                      # rota cámara por la tendencia RDA
        intensity = base_intensity + (0.15 if shot_type == "impact" else 0.0)
        # jitter determinista (sin azar): alterna +/- según el índice
        sign = 1 if i % 2 == 0 else -1
        factor = _SHOT_FACTOR.get(shot_type, 1.0) * (1.0 + sign * jitter * 0.5)
        duration_i = round(max(1.0, asl * factor), 2)
        shots.append(
            PlannedShot(
                id=f"{scene_id}::shot-{i + 1:02d}",
                scene_id=scene_id,
                index=i,
                shot_type=shot_type,
                camera_move=move,
                camera_intensity=round(min(1.0, intensity), 2),
                lighting=lighting,
                duration=duration_i,
                asset_type="image",
                reuse_key="",          # único por defecto (VIS-2 puede marcar motivos)
                fact_ids=fact_ids,
            )
        )

    return VisualPlan(
        scene_id=scene_id,
        style=style,
        reference=str(getattr(profile, "reference", "")),
        pacing_tier=pacing_tier,
        movement_tendency=movement,
        lighting_tendency=plan_lighting,
        grade=grade,
        shots=shots,
    )
