"""Runner del primer vertical funcional (composition root + presentación).

Sprint B-02: el flujo comienza con una URL real de YouTube.

    YouTube URL → Create Research → Fetch metadata → Create Source
    → Analyze (simple) → Evidence → Knowledge

El pipeline del núcleo (analyze/extract/generate) no se modifica: solo se
alimenta con el contenido obtenido de la URL.

Ejecutable con:  python -m app.cli.runner <YouTube URL>
"""

import os
import sys

from app.application.production_service import ProductionService
from app.application.research_service import ResearchService
from app.cli.llm_narrative_stage import run_llm_narrative_stage
from app.infrastructure.video import FfmpegVideoComposer
from app.infrastructure.video.media_normalizer import MediaNormalizer
from app.infrastructure.visual import CardImageRenderer
from app.infrastructure.voice import SapiSpeechSynthesizer
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
from app.infrastructure.youtube.metadata_fetcher import YouTubeMetadataFetcher
from app.infrastructure.youtube.transcript_fetcher import TranscriptFetcher


def _build_services() -> tuple[ResearchService, ProductionService, InMemoryFactRepository]:
    """Composition root: ensambla infraestructura en el núcleo.

    Ambos servicios comparten las mismas instancias de repositorio para que la
    producción lea el conocimiento que ha generado la investigación. Se expone
    también el repositorio de hechos para alimentar el Narrative Engine.
    """
    facts = InMemoryFactRepository()
    knowledge = InMemoryKnowledgeRepository()
    narratives = InMemoryNarrativeRepository()

    research = ResearchService(
        workspaces=InMemoryWorkspaceRepository(),
        researches=InMemoryResearchRepository(),
        sources=InMemorySourceRepository(),
        evidences=InMemoryEvidenceRepository(),
        facts=facts,
        claims=InMemoryClaimRepository(),
        knowledge=knowledge,
    )
    production = ProductionService(
        knowledge=knowledge,
        facts=facts,
        narratives=narratives,
        synthesizer=SapiSpeechSynthesizer(),
        renderer=CardImageRenderer(),
        composer=FfmpegVideoComposer(),
        normalizer=MediaNormalizer(),
    )
    return research, production, facts


def _source_content(metadata: dict[str, str]) -> str:
    """Compone el contenido del Source a partir de los metadatos del vídeo."""
    lines = [
        f"Título: {metadata['title']}",
        f"Canal: {metadata['channel']}",
        f"URL: {metadata['url']}",
        "Descripción:",
        metadata["description"],
    ]
    return "\n".join(line for line in lines if line.strip())


def run(url: str) -> None:
    # La consola Windows usa cp1252; aseguramos UTF-8 para títulos/descripciones reales.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    service, production, facts_repo = _build_services()
    fetcher = YouTubeMetadataFetcher()
    transcript_fetcher = TranscriptFetcher()

    print("=" * 60)
    print("DocumentaryAI — Primer vertical (Research) desde URL de YouTube")
    print("=" * 60)

    research = service.create_research(title=f"Investigación sobre vídeo: {url}")
    print(f"\n[Create Research]  id={research.id}")

    metadata = fetcher.fetch(url)
    print("[Fetch metadata]")
    print(f"    título:      {metadata['title'] or '(no disponible)'}")
    print(f"    canal:       {metadata['channel'] or '(no disponible)'}")
    desc = metadata["description"]
    print(f"    descripción: {len(desc)} caracteres" if desc else "    descripción: (no disponible)")

    # Preferimos la transcripción real; si no hay subtítulos, degradamos a la descripción.
    transcript = transcript_fetcher.fetch(url)
    if transcript:
        source_content = transcript
        print(f"[Fetch transcript] {len(transcript)} caracteres")
    else:
        source_content = _source_content(metadata)
        print("[Fetch transcript] (no disponible) -> degradación a metadatos/descripción")

    source = service.register_source(
        research_id=research.id,
        reference=url,
        content=source_content,
    )
    print(f"[Create Source]    id={source.id} (ref={source.reference})")

    observations = service.analyze_source(source.id)
    print(f"[Analyze]          {len(observations)} observación(es)")

    evidence = service.extract_evidence(source.id)
    print(f"[Evidence]         {len(evidence)} evidencia(s) con procedencia a la fuente")

    knowledge = service.generate_knowledge(research.id)
    print(f"[Knowledge]        id={knowledge.id}")
    print(f"    {knowledge.content}")
    print(f"    trazabilidad: {len(knowledge.fact_ids)} fact(s) -> evidencia -> fuente")

    # Facts -> NarrativeEngine (LLM) -> Scenes  (Sprint B-06, etapa OPCIONAL).
    # No sustituye al guion determinista; sin clave (o ante fallo) se degrada.
    output_dir = os.path.join("outputs", research.id)
    facts = facts_repo.list_by_ids(knowledge.fact_ids)
    llm_result = run_llm_narrative_stage(facts, evidence, output_dir)
    if llm_result.used_llm:
        print(
            f"[NarrativeEngine]  {llm_result.scene_count} escena(s) (LLM, "
            f"{llm_result.seconds:.1f}s) -> {output_dir}/scenes.json"
        )
        print(
            f"    procedencia: {llm_result.traced_fact_refs} ref(s) "
            "scene -> fact -> evidence -> source"
        )
    else:
        print(f"[NarrativeEngine]  {llm_result.message}")

    # B-08: la narrativa de producción es la del LLM si está disponible; ante
    # cualquier fallo se degrada al guion determinista (Voice/Images/Video la
    # consumen igual, sin cambios en sus etapas).
    doc_title = metadata["title"] or f"Documental: {research.id}"
    if llm_result.used_llm and llm_result.scenes:
        narrative = production.narrative_from_scenes(
            research.id, knowledge.id, doc_title, llm_result.scenes
        )
        narrative_source = "LLM"
    else:
        narrative = production.generate_narrative(research.id, title=doc_title)
        narrative_source = "Deterministic fallback"
    print(f"[Narrative]        fuente: {narrative_source} ({len(narrative.segments)} escena(s))")
    for segment in narrative.segments:
        preview = segment.text if len(segment.text) <= 90 else segment.text[:87] + "..."
        print(f"    [{segment.kind}] {preview}")

    voiceover = production.generate_voiceover(narrative, output_dir)
    real = sum(1 for clip in voiceover.clips if clip.synthesized)
    print(f"[Voice]            id={voiceover.id} ({len(voiceover.clips)} clip(s))")
    print(f"    audio real: {real}/{len(voiceover.clips)} -> {output_dir}/voice/")

    storyboard = production.generate_storyboard(narrative, output_dir)
    rendered = sum(1 for scene in storyboard.scenes if scene.rendered)
    print(f"[Images]           id={storyboard.id} ({len(storyboard.scenes)} imagen(es))")
    print(f"    imágenes: {rendered}/{len(storyboard.scenes)} -> {output_dir}/images/")

    print("[Video]            ensamblando con ffmpeg...")
    documentary = production.generate_video(
        narrative, storyboard, voiceover, output_dir
    )
    if documentary.rendered:
        print(f"[Video]            id={documentary.id} -> {documentary.video_path}")
    else:
        print("[Video]            (no se pudo ensamblar el vídeo)")

    print("\nFlujo completado de extremo a extremo.")


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("Uso: python -m app.cli.runner <YouTube URL>")
        raise SystemExit(2)
    run(args[0])


if __name__ == "__main__":
    main()
