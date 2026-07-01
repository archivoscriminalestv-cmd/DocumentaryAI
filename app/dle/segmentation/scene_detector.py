"""Agrupa planos en escenas y en bloques narrativos (determinista, sin invención).

- Escenas: un nuevo plano abre escena cuando cambia su estilo visual (color dominante /
  temperatura / salto de brillo).
- Bloques narrativos: se segmenta el timeline por cambios de ritmo (pacing), pero NO se
  nombran (Hook/Conflicto/…): sin comprensión semántica la confianza es nula → UNKNOWN.
"""

from app.dle import UNKNOWN
from app.dle.models import NarrativeBlock, SceneSegment, ShotAnalysis

_BRIGHTNESS_JUMP = 35.0


def group_into_scenes(shots: list[ShotAnalysis]) -> list[SceneSegment]:
    scenes: list[SceneSegment] = []
    if not shots:
        return scenes

    def _new_scene(idx: int, shot: ShotAnalysis) -> SceneSegment:
        return SceneSegment(index=idx, start=shot.start, end=shot.end, duration=shot.duration,
                            shot_indices=[shot.index], dominant_color=shot.dominant_color,
                            color_temperature=shot.color_temperature)

    current = _new_scene(0, shots[0])
    shots[0].scene_index = 0
    for shot in shots[1:]:
        changed = (
            shot.dominant_color != current.dominant_color
            or shot.color_temperature != current.color_temperature
            or abs(shot.brightness - _scene_brightness(shots, current)) > _BRIGHTNESS_JUMP
        )
        if changed:
            scenes.append(current)
            current = _new_scene(len(scenes), shot)
        else:
            current.end = shot.end
            current.duration = round(current.end - current.start, 3)
            current.shot_indices.append(shot.index)
        shot.scene_index = current.index
    scenes.append(current)
    return scenes


def _scene_brightness(shots: list[ShotAnalysis], scene: SceneSegment) -> float:
    vals = [shots[i].brightness for i in scene.shot_indices if i < len(shots)]
    return sum(vals) / len(vals) if vals else 0.0


def build_narrative_blocks(shots: list[ShotAnalysis], duration: float,
                           max_blocks: int = 5) -> list[NarrativeBlock]:
    """Segmenta por cambios de ritmo; etiqueta UNKNOWN (no se inventan categorías)."""
    if not shots:
        return []
    # Frontera donde la longitud de plano cambia bruscamente (cambio de ritmo).
    boundaries = [0]
    for i in range(1, len(shots)):
        prev, cur = shots[i - 1].duration, shots[i].duration
        if prev > 0 and (max(prev, cur) / max(0.001, min(prev, cur))) >= 2.2:
            boundaries.append(i)
    boundaries.append(len(shots))
    # Reduce a max_blocks fusionando las fronteras más débiles (mantiene las primeras).
    uniq = sorted(set(boundaries))
    while len(uniq) - 1 > max_blocks:
        uniq.pop(1)

    blocks: list[NarrativeBlock] = []
    segs = list(zip(uniq, uniq[1:]))
    for k, (a, b) in enumerate(segs):
        start = shots[a].start
        end = shots[b - 1].end
        blocks.append(NarrativeBlock(index=k, start=round(start, 3), end=round(end, 3),
                                     category=UNKNOWN, confidence=0.0,
                                     label=f"segment {k + 1}/{len(segs)}"))
    return blocks
