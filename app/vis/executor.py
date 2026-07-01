"""VIS-2 (real, mínimo): VisualPlan -> ExecutionPlan (requests para el MGL).

Impone VARIACIÓN visual obligatoria (lente/ángulo/composición no repetidos entre
planos consecutivos) y ensambla el prompt ejecutable (gramática ARCH-VIS-000 §12).
Garantiza unicidad: prompts genuinamente distintos + reuse_key vacío (=> el MGL
NO reutiliza) salvo motivos. Determinista (sin LLM/red).
"""

import hashlib

from app.vis.models import ExecutionPlan, ShotRequest, VisualPlan

_LENSES = ["ultra-wide 18mm", "wide 35mm", "normal 50mm", "tele 100mm", "super-tele 200mm", "macro"]
_ANGLES = ["eye-level", "low-angle", "high-angle", "dutch-angle", "aerial top-down", "over-the-shoulder"]
_COMPS = ["rule of thirds", "centered symmetry", "leading lines", "frame within a frame", "negative space", "layered depth"]

# Lentes coherentes por tipo de plano (HARD-3): se elige variando, pero dentro de lo razonable.
_LENS_BY_TYPE = {
    "establishing": ["ultra-wide 18mm", "wide 35mm"],
    "wide": ["wide 35mm", "ultra-wide 18mm", "normal 50mm"],
    "detail": ["macro", "tele 100mm", "normal 50mm"],
    "closeup": ["tele 100mm", "normal 50mm", "macro"],
    "action": ["wide 35mm", "tele 100mm", "normal 50mm"],
    "impact": ["tele 100mm", "wide 35mm", "super-tele 200mm"],
    "aftermath": ["wide 35mm", "ultra-wide 18mm", "normal 50mm"],
}

_NEGATIVE = (
    "text, watermark, logo, low quality, deformed, oversaturated, generic stock photo, "
    "static, flat, slideshow, powerpoint, identical framing, duplicate"
)


def _seed(shot_id: str) -> int:
    return int(hashlib.md5(shot_id.encode("utf-8")).hexdigest()[:8], 16)


def _pick(options: list[str], index: int, avoid: str | None) -> str:
    """Selección determinista que evita repetir el valor anterior."""
    choice = options[index % len(options)]
    if choice == avoid:
        choice = options[(index + 1) % len(options)]
    return choice


def _subject(scene) -> str:
    title = str(getattr(scene, "title", "")).strip()
    return title or "the subject"


def compile_execution(plan: VisualPlan, scene) -> ExecutionPlan:
    requests: list[ShotRequest] = []
    prev_lens = prev_angle = prev_comp = None
    seen_fp: set[str] = set()

    for i, shot in enumerate(plan.shots):
        lens_pool = _LENS_BY_TYPE.get(shot.shot_type, _LENSES)
        lens = _pick(lens_pool, i, prev_lens)
        angle = _pick(_ANGLES, i, prev_angle)
        comp = _pick(_COMPS, i, prev_comp)

        # Unicidad: si la terna+tipo colisiona, perturba un eje (anti-PowerPoint).
        fp = f"{shot.shot_type}|{lens}|{angle}|{comp}"
        perturb = 0
        while fp in seen_fp and perturb < len(_ANGLES):
            angle = _ANGLES[(i + perturb + 1) % len(_ANGLES)]
            fp = f"{shot.shot_type}|{lens}|{angle}|{comp}"
            perturb += 1
        seen_fp.add(fp)

        dof = "shallow depth of field" if shot.shot_type in ("detail", "closeup", "impact") else "deep focus"
        prompt = (
            f"Cinematic {shot.shot_type} shot of {_subject(scene)}, "
            f"{lens} {dof}, {comp}, {angle}, {shot.lighting}, {plan.grade}, "
            f"{plan.style} documentary photography, hyper-detailed, atmospheric, 8k"
        )

        requests.append(
            ShotRequest(
                shot_id=shot.id,
                scene_id=shot.scene_id,
                media_type=shot.asset_type,
                prompt=prompt,
                negative_prompt=_NEGATIVE,
                reuse_key=shot.reuse_key,           # "" => MGL genera único
                variation_seed=_seed(shot.id),
                motion={"move": shot.camera_move, "intensity": shot.camera_intensity},
                lens=lens,
                angle=angle,
                composition=comp,
                fingerprint=fp,
            )
        )
        prev_lens, prev_angle, prev_comp = lens, angle, comp

    return ExecutionPlan(scene_id=plan.scene_id, requests=requests)
