"""Single command: topic -> documental .mp4 (ensamblaje de SECUENCIAS, VIS).

    python -m app.cli.assemble_documentary "<topic>"

Cada escena se descompone en VARIOS planos (VIS-1 → VIS-2), cada plano genera su
asset único (MGL.generate_for_shot) y se renderiza como clip (ShotProcessor) antes
de componer el .mp4 final. El estilo visual lo marca un CinematicProfile del RDA
(el último de la biblioteca si existe; si no, uno neutro por defecto).

NO usa el research pipeline: las escenas vienen de un generador determinista
mínimo (placeholder). Camera Motion aún no implementado (still por ahora).
"""

import json
import os
import sys
from dataclasses import asdict

from app.application.documentary_assembler import DocumentaryAssembler
from app.domain.narrative.scene import Scene
from app.rda.library import ReferenceLibrary
from app.rda.models import CinematicProfile


def topic_to_scenes(topic: str) -> list[Scene]:
    topic = " ".join((topic or "").split())
    beats = [
        ("Introduction", f"In this documentary, we explore {topic}."),
        ("Background", f"To understand {topic}, we begin with its origins and context."),
        ("Key aspects", f"Several defining aspects shape how we understand {topic}."),
        ("Why it matters", f"The significance of {topic} reaches further than it first appears."),
        ("Conclusion", f"This has been an overview of {topic}."),
    ]
    return [
        Scene(id=f"scene-{i + 1:02d}", title=title, narration=narration, fact_ids=[])
        for i, (title, narration) in enumerate(beats)
    ]


def _default_profile() -> CinematicProfile:
    return CinematicProfile(
        reference="default-neutral", source_type="default", width=1920, height=1080,
        aspect_ratio="16:9", fps=24.0, duration=0.0, sample_fps=4.0, shot_count=0,
        avg_shot_length=3.0, median_shot_length=3.0, min_shot_length=2.0, max_shot_length=5.0,
        shot_length_stddev=1.0, cuts_per_minute=20.0, pacing_tier="moderate",
        shot_length_variety="moderate", brightness_mean=120.0, contrast_mean=40.0,
        lighting_tendency="balanced", warmth_mean=0.0, colorfulness_mean=25.0,
        color_temperature="neutral", saturation_tendency="moderate", motion_mean=0.04,
        movement_tendency="moderate",
    )


def _resolve_profile() -> CinematicProfile:
    """Usa el último CinematicProfile del RDA si existe; si no, uno neutro."""
    try:
        library = ReferenceLibrary()
        profiles = library.list_profiles()
        if profiles:
            data = library.load(profiles[-1])
            return CinematicProfile(**data)
    except Exception:
        pass
    return _default_profile()


def _build_assembler(output_dir: str) -> DocumentaryAssembler:
    from app.media.generation.mgl import MediaGenerationLayer
    from app.media.store.asset_store import AssetStore
    from app.infrastructure.voice import SapiSpeechSynthesizer

    mgl = MediaGenerationLayer(store=AssetStore(base_dir=os.path.join(output_dir, "assets")))
    return DocumentaryAssembler(
        mgl,
        SapiSpeechSynthesizer(),
        normalizer=_build_normalizer(),
        composer=_build_composer(),
        output_dir=output_dir,
        style="youtube_documentary",
    )


def _build_normalizer():
    try:
        from app.infrastructure.video.media_normalizer import MediaNormalizer
        return MediaNormalizer()
    except Exception:
        return None


def _build_composer():
    try:
        from app.infrastructure.video import FfmpegVideoComposer
        return FfmpegVideoComposer()
    except Exception:
        return None


def run(topic: str) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    output_dir = os.path.join("output", "documentary")
    scenes = topic_to_scenes(topic)
    profile = _resolve_profile()
    print(f"[Scenes]   {len(scenes)} escena(s) | estilo de referencia: {profile.reference}")

    result = _build_assembler(output_dir).assemble(scenes, profile=profile, topic=topic)

    print(f"[Sequence] {result.scene_count} escenas -> {result.shot_count} planos")
    print("[Assembly] " + ("OK" if result.rendered else "sin vídeo (faltan deps FFmpeg)"))
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    if result.rendered:
        print(f"\nDocumental: {result.video_path}")


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    topic = " ".join(args).strip()
    if not topic:
        print('Uso: python -m app.cli.assemble_documentary "<topic>"')
        raise SystemExit(2)
    run(topic)


if __name__ == "__main__":
    main()
