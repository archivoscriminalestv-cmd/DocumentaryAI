"""Render del NarrativeBlueprint a Markdown (NAR-001) — legible para humanos, sin prosa narrativa.

Es un resumen auditable del PLANO (no del guion): qué decide el director narrativo y por qué.
"""

from app.nar.models import NarrativeBlueprint


def render_markdown(bp: NarrativeBlueprint) -> str:
    t = bp.totals or {}
    lines = [
        f"# Narrative Blueprint — {bp.title or bp.case_id}",
        "",
        f"- versión: `{bp.schema_version}` · género: `{bp.genre}`",
        f"- estructura: **{bp.structure}**",
        f"- razón: {bp.structure_reason}",
    ]
    if bp.timeline_decision:
        lines.append(f"- orden temporal: **{bp.timeline_decision.order}** "
                     f"({bp.timeline_decision.reason})")
    if bp.emotion_curve:
        lines.append(f"- arco emocional: **{bp.emotion_curve.arc_type}** "
                     f"(pico en segmento {bp.emotion_curve.peak_index})")
    lines += [
        f"- totales: {t.get('segments')} segmentos · {t.get('acts')} actos · "
        f"{t.get('total_suggested_seconds')}s sugeridos · pico {t.get('tension_peak')}",
        f"- mecanismos: {t.get('hooks')} hooks · {t.get('reveals')} reveals · "
        f"{t.get('foreshadows')} foreshadows · {t.get('cliffhangers')} cliffhangers · "
        f"{t.get('payoffs')} payoffs",
        f"- preguntas abiertas: {t.get('viewer_questions')} · recreaciones: {t.get('recreations')}",
        "",
        "> El NAR decide CÓMO contar la historia. No escribe texto (sin guion, sin IA).",
        "",
    ]

    # Estructuras candidatas (trazabilidad de la selección)
    lines.append("## Estructuras candidatas")
    for c in bp.candidates:
        mark = "✓" if c.selected else " "
        lines.append(f"- [{mark}] **{c.structure}** — score {c.score}")
    lines.append("")

    # Segmentos
    lines.append("## Segmentos")
    lines.append("")
    lines.append("| # | beat | propósito | emoción | tensión | dur(s) | narración | evidencia |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for s in bp.segments:
        ev = ", ".join(f"{e.dimension}:{e.use}" for e in s.evidence) or "—"
        rec = " ⟲" if s.recreations else ""
        lines.append(f"| {s.index} | {s.beat} | {s.purpose} | {s.emotion} | {s.tension} | "
                     f"{s.suggested_duration_seconds} | {s.narration.mode}/{s.narration.intent} | "
                     f"{ev}{rec} |")
    lines.append("")

    # Devices
    if bp.devices_applied:
        lines.append("## Dispositivos aplicados")
        for d in bp.devices_applied:
            lines.append(f"- **{d['type']}** → segmentos {d['target_segments']} — {d['reason']}")
        lines.append("")

    # Preguntas abiertas
    if bp.viewer_questions:
        lines.append("## Preguntas para el espectador (estructuradas)")
        for q in bp.viewer_questions:
            lines.append(f"- `{q.type}` sobre **{q.target}** "
                         f"(origen: {q.origin}; abierta en seg. {q.opened_in})")
        lines.append("")

    # Provenance
    if bp.provenance:
        p = bp.provenance
        lines.append("## Procedencia (trazabilidad)")
        lines.append(f"- entradas presentes: {', '.join(p.inputs_present) or '—'}")
        lines.append(f"- entradas ausentes: {', '.join(p.inputs_missing) or '—'}")
        lines.append(f"- conocimiento usado: {', '.join(p.knowledge_used) or '—'}")
        lines.append(f"- entradas UNKNOWN (no se inventan): {', '.join(p.unknown_inputs) or '—'}")
        lines.append("")

    return "\n".join(lines)
