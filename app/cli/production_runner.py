"""Production runner — composition root de la pila de media C-09…C-11.5.

Cablea, de forma ADITIVA (sin tocar el runner E2E existente ni el dominio):

    input (URL de YouTube o texto)
      → Research (facts trazables)
      → Scene[]            (puente determinista facts → escenas)
      → DirectorService    (C-08: DirectedScene[])
      → MediaStyleService  (C-09: MediaStyledScene[])
      → FinalRenderService (C-10: render + caché)
      → ExperimentRunner   (C-11: versión + métricas)

Identidad de voz GLOBAL e INMUTABLE (C-11) y selección de sintetizador por
secretos/entorno (C-11.5): ElevenLabs si hay clave; SAPI como fallback en DEV.
Las dependencias opcionales (Pillow/ffmpeg) degradan con elegancia: el pipeline
SIEMPRE produce su informe JSON.

Ejecutable:  python -m app.cli.production_runner "<YouTube URL | tema>"
"""

import json
import os
import sys

from app.application.channel_identity import CHANNEL_IDENTITY
from app.application.director_service import DirectorService
from app.application.emotional_narrative_director import EmotionalNarrativeDirector
from app.application.experiment_service import ExperimentRunner, compact_output
from app.application.final_render_service import FinalRenderService
from app.application.media_style_service import MediaStyleService
from app.application.narrative_arc import NarrativeArcBuilder
from app.application.research_service import ResearchService
from app.infrastructure.config.runtime_secrets import SecretsManager
from app.infrastructure.memory.repositories import (
    InMemoryClaimRepository,
    InMemoryEvidenceRepository,
    InMemoryFactRepository,
    InMemoryKnowledgeRepository,
    InMemoryNarrativeRepository,
    InMemoryResearchRepository,
    InMemorySourceRepository,
    InMemoryWorkspaceRepository,
)
from app.infrastructure.visual.image_cache import ImageCache
from app.infrastructure.voice.narrator import build_speech_synthesizer, runtime_status
from app.infrastructure.voice.voice_cache import VoiceCache


def _build_research_service() -> tuple[ResearchService, InMemoryFactRepository]:
    facts = InMemoryFactRepository()
    research = ResearchService(
        workspaces=InMemoryWorkspaceRepository(),
        researches=InMemoryResearchRepository(),
        sources=InMemorySourceRepository(),
        evidences=InMemoryEvidenceRepository(),
        facts=facts,
        claims=InMemoryClaimRepository(),
        knowledge=InMemoryKnowledgeRepository(),
    )
    return research, facts


def _resolve_source(arg: str) -> tuple[str, str]:
    """Devuelve (reference, content). Para una URL de YouTube intenta transcripción/
    descripción; en otro caso trata el argumento como contenido directo."""
    if arg.startswith("http") and "youtu" in arg:
        from app.infrastructure.youtube.metadata_fetcher import YouTubeMetadataFetcher
        from app.infrastructure.youtube.transcript_fetcher import TranscriptFetcher

        transcript = TranscriptFetcher().fetch(arg)
        if transcript:
            return arg, transcript
        meta = YouTubeMetadataFetcher().fetch(arg)
        content = "\n".join(
            line
            for line in (
                f"Título: {meta['title']}",
                f"Canal: {meta['channel']}",
                f"URL: {meta['url']}",
                meta["description"],
            )
            if line.strip()
        )
        return arg, content or arg
    return "input:text", arg


def _build_llm():
    """Proveedor LLM si está configurado/con clave; si no, None (degradación)."""
    try:
        from app.infrastructure.llm.factory import create_llm_provider

        return create_llm_provider()
    except Exception:
        return None


def _build_composer():
    """FfmpegVideoComposer si su dependencia está disponible; si no, None."""
    try:
        from app.infrastructure.video import FfmpegVideoComposer

        return FfmpegVideoComposer()
    except Exception:
        return None


def _build_normalizer():
    """MediaNormalizer si su dependencia está disponible; si no, None."""
    try:
        from app.infrastructure.video.media_normalizer import MediaNormalizer

        return MediaNormalizer()
    except Exception:
        return None


def _build_image_renderer():
    """CardImageRenderer si Pillow está disponible; si no, None."""
    try:
        from app.infrastructure.visual import CardImageRenderer

        return CardImageRenderer()
    except Exception:
        return None


def main(arg: str) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    # 1) Runtime config (DEV / PROD) + secretos.
    secrets = SecretsManager()
    secrets.load_env()
    status = runtime_status(secrets)
    print("[Runtime]", json.dumps(status, ensure_ascii=False))

    # 2) Voz: ElevenLabs (si hay clave) o SAPI (fallback DEV). En PROD sin clave,
    #    build_speech_synthesizer lanza RuntimeError (fallo duro, por diseño).
    synthesizer = build_speech_synthesizer(secrets)

    # 3) Research → facts trazables.
    research_service, facts_repo = _build_research_service()
    research = research_service.create_research(title="Producción documental")
    reference, content = _resolve_source(arg)
    source = research_service.register_source(research.id, reference, content)
    research_service.extract_evidence(source.id)
    knowledge = research_service.generate_knowledge(research.id)
    facts = facts_repo.list_by_ids(knowledge.fact_ids)
    print(f"[Research] facts={len(facts)}")

    # 4) Arco (C-12) → narración emocional LLM (C-13) → Director (C-08) → MediaStyle (C-09).
    scenes = NarrativeArcBuilder().narrative_scenes(facts)
    scenes = EmotionalNarrativeDirector(_build_llm()).direct(scenes)
    directed = DirectorService().direct(scenes)
    styled = MediaStyleService().style(directed)
    print(f"[Media] scenes styled={len(styled)}")

    # 5) Render final (C-10) con identidad de canal (C-11) + cachés.
    render_service = FinalRenderService(
        voice_cache=VoiceCache(synthesizer, base_dir="cache"),
        image_cache=ImageCache(_build_image_renderer(), base_dir="cache"),
        composer=_build_composer(),
        normalizer=_build_normalizer(),
        voice_id=CHANNEL_IDENTITY.voice_id,
        model=CHANNEL_IDENTITY.model,
        output_dir=os.path.join("output", "render", research.id),
    )

    # 6) Experimentación (C-11): versión + métricas.
    report = ExperimentRunner(render_service).run(styled)

    # 7) Salida final (contrato C-11).
    print("\n=== FINAL REPORT ===")
    print(json.dumps(compact_output(report, comparison_available=True), ensure_ascii=False))


if __name__ == "__main__":
    text = " ".join(sys.argv[1:]).strip()
    if not text:
        print('Uso: python -m app.cli.production_runner "<YouTube URL | tema>"')
        raise SystemExit(2)
    main(text)
