"""Ejemplo: compila el documental "Coquito" en VisualGenerationRequests (VSC).

    python -m app.cli.compile_coquito

Recorre toda la cadena VIS-1 -> VAI -> VSC para cada plano de cada escena,
preservando la continuidad por escena y demostrando la caché de assets por
``reuse_key`` (una localización recurrente se reutiliza). Imprime las peticiones
de generación normalizadas — entrada del próximo sprint (proveedor real).
"""

import json
import sys
from dataclasses import asdict

from app.cli.coquito import coquito_documentary
from app.rda.models import CinematicProfile
from app.vai import VisualDirector
from app.vis import build_visual_plan
from app.vsc import (
    CachingVisualProvider,
    GlobalStyle,
    MockVisualProvider,
    VisualSceneCompiler,
    to_vai_context,
)


def neutral_profile() -> CinematicProfile:
    return CinematicProfile(
        reference="coquito", source_type="default", width=1280, height=720, aspect_ratio="16:9",
        fps=25.0, duration=0.0, sample_fps=4.0, shot_count=0, avg_shot_length=3.0,
        median_shot_length=3.0, min_shot_length=2.0, max_shot_length=5.0, shot_length_stddev=1.0,
        cuts_per_minute=20.0, pacing_tier="moderate", shot_length_variety="varied",
        brightness_mean=110.0, contrast_mean=40.0, lighting_tendency="balanced", warmth_mean=-10.0,
        colorfulness_mean=18.0, color_temperature="cool", saturation_tendency="muted",
        motion_mean=0.04, movement_tendency="moderate",
    )


def build_requests(sde=None, *, character_name: str = "", identity: str = ""):
    """VIS-1 -> VAI -> [SDE] -> VSC para todo el documental Coquito (26 planos).

    Si ``sde`` (ShotDiversityEngine) se proporciona, cada ShotExecutionRequest del VAI
    pasa por el SDE ANTES del VSC para diversificar la composición (aditivo; el VSC y
    todo lo demás quedan intactos). Sin ``sde``, el comportamiento es el de siempre.
    """
    profile = neutral_profile()
    director = VisualDirector()
    compiler = VisualSceneCompiler()
    global_style = GlobalStyle()

    all_requests = []
    for scene, svc, duration in coquito_documentary():
        plan = build_visual_plan(profile, scene, scene_duration=duration)
        # Localización recurrente: los planos de contexto (establishing/wide) reutilizan
        # el mismo asset de localización (caché por reuse_key = identidad de escena).
        for ps in plan.shots:
            if ps.shot_type in ("establishing", "wide"):
                ps.reuse_key = svc.identity
        vai_ctx = to_vai_context(svc, subject=scene.title)
        for ps in plan.shots:
            req = director.direct(ps, vai_ctx)
            if sde is not None:
                from app.sde import SDEContext
                ctx = SDEContext(
                    scene_id=scene.id, documentary_style=svc.documentary_style,
                    location=svc.location, color_palette=svc.color_palette,
                    time_of_day=svc.time_of_day, weather=svc.weather,
                    lighting=svc.lighting_language, character_name=character_name,
                    identity=identity, shot_role=getattr(ps, "shot_type", ""),
                )
                req = sde.process(req, ctx)
            all_requests.append(compiler.compile(req, svc, global_style))
    return all_requests


def build_shot_contexts():
    """Metadatos por plano alineados con ``build_requests`` (para el CME).

    Devuelve, en el MISMO orden que build_requests, un dict por plano con:
    scene_id, documentary_style, shot_role y shot_duration (escena/Nº planos).
    Determinista; re-deriva el plan VIS sin tocar nada.
    """
    profile = neutral_profile()
    out = []
    for scene, svc, duration in coquito_documentary():
        plan = build_visual_plan(profile, scene, scene_duration=duration)
        count = len(plan.shots) or 1
        for ps in plan.shots:
            out.append({
                "scene_id": scene.id,
                "documentary_style": svc.documentary_style,
                "shot_role": getattr(ps, "shot_type", ""),
                "shot_duration": round(duration / count, 3),
            })
    return out


def run() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    requests = build_requests()
    print(f"[VSC] Coquito -> {len(requests)} visual generation requests\n")
    print(json.dumps([asdict(r) for r in requests], ensure_ascii=False, indent=2))

    # Demostración de caché: ejecuta las peticiones por un proveedor mock con caché.
    provider = CachingVisualProvider(MockVisualProvider())
    assets = [provider.generate(r) for r in requests]
    generated = sum(1 for a in assets if not a.cached)
    reused = sum(1 for a in assets if a.cached)
    print(f"\n[Cache] {len(requests)} requests -> {generated} generados, {reused} reutilizados "
          f"(localización recurrente: {provider.cache.has('corner_finestrelles_almassora')})")


if __name__ == "__main__":
    run()
