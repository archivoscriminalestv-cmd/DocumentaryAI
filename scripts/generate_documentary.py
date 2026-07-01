"""Genera un documental completo de extremo a extremo y persiste todo.

Orquesta el mismo pipeline que ``app.cli.runner`` (reutiliza servicios y
adaptadores sin modificarlos) pero, además, guarda cada artefacto intermedio en
``outputs/<research-id>/`` y produce un ``REPORT.md`` con etapas, tiempos y
degradaciones.

Uso:  python -m scripts.generate_documentary <YouTube URL>
"""

import json
import os
import sys
import time
from dataclasses import asdict
from datetime import datetime

from app.application.production_service import ProductionService
from app.application.research_service import ResearchService
from app.cli.llm_narrative_stage import run_llm_narrative_stage
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
from app.infrastructure.video import FfmpegVideoComposer
from app.infrastructure.visual import CardImageRenderer
from app.infrastructure.voice import SapiSpeechSynthesizer
from app.infrastructure.youtube.metadata_fetcher import YouTubeMetadataFetcher
from app.infrastructure.youtube.transcript_fetcher import TranscriptFetcher


class Timed:
    """Mide la duración de una etapa y la registra."""

    def __init__(self, log: list[dict], stage: str) -> None:
        self._log = log
        self._stage = stage
        self._start = 0.0

    def __enter__(self) -> "Timed":
        self._start = time.perf_counter()
        print(f"[{self._stage}] ...", flush=True)
        return self

    def __exit__(self, *exc) -> None:
        seconds = time.perf_counter() - self._start
        self._log.append({"stage": self._stage, "seconds": seconds})
        print(f"[{self._stage}] {seconds:.1f}s", flush=True)


def _write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def _write_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)


def run(url: str) -> str:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    timings: list[dict] = []
    notes: list[str] = []

    # --- Composition root (idéntico al runner) -------------------------------
    facts_repo = InMemoryFactRepository()
    knowledge_repo = InMemoryKnowledgeRepository()
    narratives_repo = InMemoryNarrativeRepository()
    research_svc = ResearchService(
        workspaces=InMemoryWorkspaceRepository(),
        researches=InMemoryResearchRepository(),
        sources=InMemorySourceRepository(),
        evidences=InMemoryEvidenceRepository(),
        facts=facts_repo,
        claims=InMemoryClaimRepository(),
        knowledge=knowledge_repo,
    )
    production = ProductionService(
        knowledge=knowledge_repo,
        facts=facts_repo,
        narratives=narratives_repo,
        synthesizer=SapiSpeechSynthesizer(),
        renderer=CardImageRenderer(),
        composer=FfmpegVideoComposer(),
    )
    metadata_fetcher = YouTubeMetadataFetcher()
    transcript_fetcher = TranscriptFetcher()

    started_at = datetime.now()
    research = research_svc.create_research(title=f"Documental: {url}")
    output_dir = os.path.join("outputs", research.id)
    os.makedirs(output_dir, exist_ok=True)
    print("=" * 64)
    print(f"DocumentaryAI — generación E2E | research={research.id}")
    print("=" * 64)

    # --- Metadata ------------------------------------------------------------
    with Timed(timings, "Metadata"):
        metadata = metadata_fetcher.fetch(url)
    _write_json(os.path.join(output_dir, "metadata.json"), metadata)

    # --- Transcript ----------------------------------------------------------
    with Timed(timings, "Transcript"):
        transcript = transcript_fetcher.fetch(url)
    if transcript:
        source_content = transcript
    else:
        lines = [
            f"Título: {metadata['title']}",
            f"Canal: {metadata['channel']}",
            f"URL: {metadata['url']}",
            "Descripción:",
            metadata["description"],
        ]
        source_content = "\n".join(line for line in lines if line.strip())
        notes.append(
            "Transcript: sin subtítulos disponibles -> degradación a "
            "metadatos/descripción."
        )
    _write_text(os.path.join(output_dir, "transcript.txt"), source_content)

    # --- Source / Evidence ---------------------------------------------------
    with Timed(timings, "Evidence"):
        source = research_svc.register_source(
            research_id=research.id, reference=url, content=source_content
        )
        evidence = research_svc.extract_evidence(source.id)
    _write_json(
        os.path.join(output_dir, "evidence.json"),
        [asdict(e) for e in evidence],
    )

    # --- Knowledge (genera Facts internamente) -------------------------------
    with Timed(timings, "Knowledge"):
        knowledge = research_svc.generate_knowledge(research.id)
    facts = facts_repo.list_by_ids(knowledge.fact_ids)
    _write_json(os.path.join(output_dir, "facts.json"), [asdict(f) for f in facts])
    _write_json(os.path.join(output_dir, "knowledge.json"), asdict(knowledge))

    # --- Narrative Engine (LLM, OPCIONAL) ------------------------------------
    # Facts -> Scenes. Sin ANTHROPIC_API_KEY (o ante fallo) se degrada al guion
    # determinista; persiste scenes.json / narrative_llm.md / prompt.md /
    # response.json y conserva procedencia Scene -> Fact -> Evidence -> Source.
    with Timed(timings, "NarrativeLLM"):
        llm_result = run_llm_narrative_stage(facts, evidence, output_dir)
    if llm_result.used_llm:
        notes.append(
            f"NarrativeEngine (LLM): {llm_result.scene_count} escena(s), "
            f"{llm_result.traced_fact_refs} ref(s) de procedencia."
        )
    else:
        notes.append(f"NarrativeEngine (LLM): {llm_result.message}")

    # --- Narrative de producción (LLM si está; si no, determinista) ----------
    # B-08: la narrativa que alimenta Voice/Images/Video es la del LLM cuando
    # está disponible; ante cualquier fallo se degrada al guion determinista.
    doc_title = metadata["title"] or f"Documental: {research.id}"
    with Timed(timings, "Narrative"):
        if llm_result.used_llm and llm_result.scenes:
            narrative = production.narrative_from_scenes(
                research.id, knowledge.id, doc_title, llm_result.scenes
            )
            narrative_source = "LLM"
        else:
            narrative = production.generate_narrative(research.id, title=doc_title)
            narrative_source = "Deterministic fallback"
    print(f"[Narrative]        fuente: {narrative_source} ({len(narrative.segments)} escena(s))")
    _write_json(os.path.join(output_dir, "narrative.json"), asdict(narrative))
    _write_text(
        os.path.join(output_dir, "narrative_script.txt"), narrative.script
    )

    # --- Voice ---------------------------------------------------------------
    with Timed(timings, "Voice"):
        voiceover = production.generate_voiceover(narrative, output_dir)
    voice_real = sum(1 for c in voiceover.clips if c.synthesized)
    _write_json(os.path.join(output_dir, "voice.json"), asdict(voiceover))
    if voice_real < len(voiceover.clips):
        notes.append(
            f"Voice: {len(voiceover.clips) - voice_real}/{len(voiceover.clips)} "
            "clip(s) sin audio real (degradación a texto)."
        )

    # --- Images --------------------------------------------------------------
    with Timed(timings, "Images"):
        storyboard = production.generate_storyboard(narrative, output_dir)
    img_real = sum(1 for s in storyboard.scenes if s.rendered)
    _write_json(os.path.join(output_dir, "storyboard.json"), asdict(storyboard))
    if img_real < len(storyboard.scenes):
        notes.append(
            f"Images: {len(storyboard.scenes) - img_real}/{len(storyboard.scenes)} "
            "imagen(es) no renderizada(s)."
        )

    # --- Video ---------------------------------------------------------------
    with Timed(timings, "Video"):
        documentary = production.generate_video(
            narrative, storyboard, voiceover, output_dir
        )
    _write_json(os.path.join(output_dir, "documentary.json"), asdict(documentary))
    if not documentary.rendered:
        notes.append("Video: ffmpeg no pudo ensamblar el vídeo.")

    finished_at = datetime.now()

    # --- REPORT.md -----------------------------------------------------------
    _write_report(
        output_dir=output_dir,
        url=url,
        metadata=metadata,
        research_id=research.id,
        transcript_chars=len(source_content),
        transcript_real=bool(transcript),
        evidence=evidence,
        facts=facts,
        knowledge=knowledge,
        narrative=narrative,
        narrative_source=narrative_source,
        llm_result=llm_result,
        voiceover=voiceover,
        storyboard=storyboard,
        documentary=documentary,
        timings=timings,
        notes=notes,
        started_at=started_at,
        finished_at=finished_at,
    )

    print(f"\nDocumental generado en: {output_dir}")
    print(f"Vídeo: {documentary.video_path} (rendered={documentary.rendered})")
    print("Flujo completado de extremo a extremo.")
    return output_dir


def _fmt(seconds: float) -> str:
    return f"{seconds:.1f}s"


def _video_bytes(path: str) -> int:
    return os.path.getsize(path) if os.path.exists(path) else 0


def _write_report(**ctx) -> None:
    o = ctx
    total = sum(t["seconds"] for t in o["timings"])
    lines: list[str] = []
    lines.append(f"# REPORT — {o['metadata']['title'] or '(sin título)'}")
    lines.append("")
    lines.append(f"- **Research ID:** `{o['research_id']}`")
    lines.append(f"- **Fuente:** {o['url']}")
    lines.append(f"- **Canal:** {o['metadata']['channel'] or '(no disponible)'}")
    lines.append(f"- **Narrative source:** {o['narrative_source']}")
    lines.append(f"- **Inicio:** {o['started_at'].isoformat(timespec='seconds')}")
    lines.append(f"- **Fin:** {o['finished_at'].isoformat(timespec='seconds')}")
    lines.append(f"- **Duración total del pipeline:** {_fmt(total)}")
    lines.append("")

    lines.append("## Pipeline")
    lines.append("")
    lines.append("```")
    lines.append("YouTube URL → Transcript → Evidence → Facts → Knowledge")
    lines.append("           → Narrative (LLM si disponible; si no, determinista)")
    lines.append("           → Voice → Images → Video")
    lines.append("```")
    lines.append("")

    lines.append("## Etapas")
    lines.append("")
    lines.append("| Etapa | Resultado | Tiempo |")
    lines.append("|-------|-----------|--------|")
    stage_detail = {
        "Metadata": f"título y descripción ({len(o['metadata']['description'])} chars)",
        "Transcript": (
            f"{o['transcript_chars']} chars "
            + ("(subtítulos reales)" if o["transcript_real"] else "(fallback metadatos)")
        ),
        "Evidence": f"{len(o['evidence'])} evidencia(s)",
        "Knowledge": f"{len(o['facts'])} hecho(s) -> 1 knowledge",
        "NarrativeLLM": (
            f"LLM: {o['llm_result'].scene_count} escena(s), "
            f"{o['llm_result'].traced_fact_refs} ref(s) de procedencia"
            if o["llm_result"].used_llm
            else f"fallback determinista ({o['llm_result'].reason})"
        ),
        "Narrative": f"{len(o['narrative'].segments)} escena(s)",
        "Voice": (
            f"{sum(1 for c in o['voiceover'].clips if c.synthesized)}/"
            f"{len(o['voiceover'].clips)} clip(s) con audio real"
        ),
        "Images": (
            f"{sum(1 for s in o['storyboard'].scenes if s.rendered)}/"
            f"{len(o['storyboard'].scenes)} imagen(es)"
        ),
        "Video": (
            f"{'OK' if o['documentary'].rendered else 'FALLO'} "
            f"({_video_bytes(o['documentary'].video_path)} bytes)"
        ),
    }
    by_stage = {t["stage"]: t["seconds"] for t in o["timings"]}
    for stage in [
        "Metadata", "Transcript", "Evidence", "Knowledge",
        "NarrativeLLM", "Narrative", "Voice", "Images", "Video",
    ]:
        lines.append(
            f"| {stage} | {stage_detail[stage]} | {_fmt(by_stage.get(stage, 0.0))} |"
        )
    lines.append("")

    lines.append("## Artefactos")
    lines.append("")
    artifacts = [
        ("metadata.json", "Metadatos del vídeo de YouTube."),
        ("transcript.txt", "Transcripción usada como Source."),
        ("evidence.json", "Evidencias extraídas (con procedencia a la fuente)."),
        ("facts.json", "Hechos derivados de las evidencias."),
        ("knowledge.json", "Knowledge consolidado y su trazabilidad a hechos."),
        ("scenes.json", "Escenas del LLM con procedencia Scene→Fact→Evidence→Source (solo ruta LLM)."),
        ("narrative_llm.md", "Guion del LLM en Markdown legible (solo ruta LLM)."),
        ("prompt.md", "Prompt exacto enviado al LLM (solo ruta LLM)."),
        ("response.json", "Respuesta cruda de Claude (solo ruta LLM)."),
        ("narrative.json", "Guion de PRODUCCIÓN segmentado (LLM o determinista, según fuente)."),
        ("narrative_script.txt", "Guion completo en texto plano."),
        ("voice.json", "Manifiesto de clips de locución."),
        ("voice/", "Audio WAV por escena."),
        ("storyboard.json", "Manifiesto de imágenes por escena."),
        ("images/", "Imágenes PNG por escena."),
        ("documentary.json", "Metadatos del vídeo final."),
        ("documentary.mp4", "**Documental final.**"),
        ("REPORT.md", "Este informe."),
    ]
    for name, desc in artifacts:
        lines.append(f"- `{name}` — {desc}")
    lines.append("")

    lines.append("## Guion narrado")
    lines.append("")
    for index, segment in enumerate(o["narrative"].segments):
        lines.append(f"**Escena {index} · {segment.kind}**")
        lines.append("")
        lines.append(f"> {segment.text}")
        lines.append("")

    lines.append("## Degradaciones / fallbacks")
    lines.append("")
    if o["notes"]:
        for note in o["notes"]:
            lines.append(f"- {note}")
    else:
        lines.append("- Ninguna. Todas las etapas se completaron sin degradación.")
    lines.append("")

    _write_text(os.path.join(o["output_dir"], "REPORT.md"), "\n".join(lines))


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("Uso: python -m scripts.generate_documentary <YouTube URL>")
        raise SystemExit(2)
    run(args[0])


if __name__ == "__main__":
    main()
