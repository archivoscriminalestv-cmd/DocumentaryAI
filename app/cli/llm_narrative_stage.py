"""Etapa opcional Facts -> NarrativeEngine (LLM) -> Scenes (Sprint B-06).

Vive en la capa de composición (CLI): orquesta el motor de aplicación, decide
LLM vs. degradación y persiste los artefactos. Reutilizada por el runner y por
``scripts/generate_documentary.py`` para no esparcir la lógica ni el modelo.

Contrato de degradación (decisión del Principal Architect):
- Sin ``ANTHROPIC_API_KEY`` (o si el LLM falla): no se rompe nada, se registra
  un mensaje claro y se cae al guion determinista existente (que corre aparte).
- Con clave: se genera el guion con el LLM y se persiste todo, preservando la
  procedencia completa Scene -> Fact IDs -> Evidence IDs -> Source IDs.
"""

import json
import os
import time
from dataclasses import dataclass, field
from typing import Callable

from app.application.narrative_engine import NARRATIVE_PROMPT, NarrativeEngine
from app.domain.evidence import Evidence
from app.domain.fact import Fact
from app.domain.narrative.scene import Scene
from app.infrastructure.llm import create_llm_provider


@dataclass
class LLMStageResult:
    used_llm: bool
    reason: str  # "ok" | "no_api_key" | "llm_error"
    seconds: float = 0.0
    scene_count: int = 0
    traced_fact_refs: int = 0
    scenes: list[Scene] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    message: str = ""


def _provenance(scene: Scene, fact_to_ev: dict, ev_to_src: dict) -> dict:
    evidence_ids: list[str] = []
    for fid in scene.fact_ids:
        ev = fact_to_ev.get(fid)
        if ev is not None and ev not in evidence_ids:
            evidence_ids.append(ev)
    source_ids: list[str] = []
    for ev in evidence_ids:
        src = ev_to_src.get(ev)
        if src is not None and src not in source_ids:
            source_ids.append(src)
    return {
        "fact_ids": scene.fact_ids,
        "evidence_ids": evidence_ids,
        "source_ids": source_ids,
    }


def _write_scenes_json(path: str, scenes, fact_to_ev, ev_to_src) -> None:
    payload = {
        "scenes": [
            {
                "id": s.id,
                "title": s.title,
                "narration": s.narration,
                "provenance": _provenance(s, fact_to_ev, ev_to_src),
            }
            for s in scenes
        ]
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def _write_narrative_md(path: str, scenes, fact_to_ev, ev_to_src) -> None:
    lines = ["# Narrativa (Narrative Engine — LLM)", ""]
    for index, scene in enumerate(scenes):
        prov = _provenance(scene, fact_to_ev, ev_to_src)
        lines.append(f"## Escena {index + 1}: {scene.title}")
        lines.append("")
        lines.append(scene.narration)
        lines.append("")
        lines.append(
            f"> Procedencia — facts: {', '.join(prov['fact_ids']) or '—'} "
            f"· evidence: {', '.join(prov['evidence_ids']) or '—'} "
            f"· sources: {', '.join(prov['source_ids']) or '—'}"
        )
        lines.append("")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def run_llm_narrative_stage(
    facts: list[Fact],
    evidence: list[Evidence],
    output_dir: str,
    llm_client: object | None = None,
    log: Callable[[str], None] = print,
) -> LLMStageResult:
    """Ejecuta la etapa LLM si procede; persiste artefactos; nunca rompe el flujo."""
    # El proveedor se resuelve por configuración (factory). Si no hay ninguno
    # disponible (sin clave / proveedor desconocido), se degrada al guion
    # determinista existente sin romper el pipeline (requisito de fallback).
    if llm_client is not None:
        client = llm_client
    else:
        client = create_llm_provider()
        if client is None:
            msg = (
                "No hay proveedor LLM disponible (revisa config.AI_PROVIDER y la "
                "clave de API) -> se usa el guion determinista existente (fallback)."
            )
            log(msg)
            return LLMStageResult(used_llm=False, reason="no_api_key", message=msg)

    os.makedirs(output_dir, exist_ok=True)
    fact_to_ev = {f.id: f.evidence_id for f in facts}
    ev_to_src = {e.id: e.source_id for e in evidence}

    try:
        engine = NarrativeEngine(llm=client)
        start = time.perf_counter()
        scenes = engine.generate(facts)
        seconds = time.perf_counter() - start
    except Exception as exc:  # cualquier fallo del LLM -> fallback, sin romper
        msg = f"Fallo del Narrative Engine ({exc}) -> fallback al guion determinista."
        log(msg)
        return LLMStageResult(used_llm=False, reason="llm_error", message=msg)

    # Persistencia de artefactos (requisitos 7-9).
    artifacts: list[str] = []

    system = getattr(client, "last_system", NARRATIVE_PROMPT)
    user = getattr(client, "last_user", "")
    prompt_path = os.path.join(output_dir, "prompt.md")
    with open(prompt_path, "w", encoding="utf-8") as handle:
        handle.write("# Prompt del Narrative Engine\n\n## System\n\n")
        handle.write(system or "")
        handle.write("\n\n## User\n\n```json\n")
        handle.write(user or "")
        handle.write("\n```\n")
    artifacts.append(prompt_path)

    raw = getattr(client, "last_response", None)
    if raw is not None:
        response_path = os.path.join(output_dir, "response.json")
        with open(response_path, "w", encoding="utf-8") as handle:
            json.dump(raw, handle, ensure_ascii=False, indent=2)
        artifacts.append(response_path)

    scenes_path = os.path.join(output_dir, "scenes.json")
    _write_scenes_json(scenes_path, scenes, fact_to_ev, ev_to_src)
    artifacts.append(scenes_path)

    md_path = os.path.join(output_dir, "narrative_llm.md")
    _write_narrative_md(md_path, scenes, fact_to_ev, ev_to_src)
    artifacts.append(md_path)

    traced = sum(len(s.fact_ids) for s in scenes)
    return LLMStageResult(
        used_llm=True,
        reason="ok",
        seconds=seconds,
        scene_count=len(scenes),
        traced_fact_refs=traced,
        scenes=scenes,
        artifacts=artifacts,
        message=f"{len(scenes)} escena(s) generadas por el LLM.",
    )
