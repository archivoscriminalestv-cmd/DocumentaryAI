"""Persistencia del CRE: escribe los artefactos de investigación.

Genera, en un directorio por personaje:
- ``character_bible.json``   (fuente de verdad, reproducible, versionada)
- ``research_manifest.json`` (proveedores consultados + sello temporal)
- ``research_report.md``     (resumen legible)

La Character Bible es reproducible (mismo input → mismo JSON). La marca de tiempo
vive SOLO en el manifest, para no romper la reproducibilidad de la bible.
"""

import json
import os
import time

from app.cre.models import CharacterBible


def write_outputs(
    out_dir: str, bible: CharacterBible, manifest: dict, *, generated_at: float | None = None
) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    bible_path = os.path.join(out_dir, "character_bible.json")
    manifest_path = os.path.join(out_dir, "research_manifest.json")
    report_path = os.path.join(out_dir, "research_report.md")

    with open(bible_path, "w", encoding="utf-8") as handle:
        json.dump(bible.to_dict(), handle, ensure_ascii=False, indent=2, sort_keys=True)

    manifest_out = dict(manifest)
    manifest_out["generated_at"] = generated_at if generated_at is not None else time.time()
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest_out, handle, ensure_ascii=False, indent=2)

    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(_render_report(bible, manifest))

    return {"bible": bible_path, "manifest": manifest_path, "report": report_path}


def _render_report(bible: CharacterBible, manifest: dict) -> str:
    from dataclasses import fields

    ident = bible.identity
    available = [p["provider"] for p in manifest.get("providers", []) if p.get("available")]
    pending = [p["provider"] for p in manifest.get("providers", []) if not p.get("available")]

    # Cobertura: campos con dato vs. vacíos, recorriendo todas las secciones tipadas.
    sections = {
        "identity": bible.identity,
        "biography": bible.biography,
        "physical_appearance": bible.physical_appearance,
        "behaviour": bible.behaviour,
        "voice": bible.voice,
        "environment": bible.environment,
    }
    found: list[str] = []
    empty: list[str] = []
    for section_name, obj in sections.items():
        for f in fields(obj):
            value = getattr(obj, f.name)
            target = found if value not in ("", None, []) else empty
            target.append(f"{section_name}.{f.name}")
    coverage = (len(found) / (len(found) + len(empty)) * 100.0) if (found or empty) else 0.0

    def _filled(value) -> str:
        if isinstance(value, list):
            return f"{len(value)} entrada(s)" if value else "—"
        return str(value) if value not in ("", None) else "—"

    lines = [
        f"# Character Bible — {ident.canonical_name or '(sin nombre)'}",
        "",
        f"- schema_version: `{bible.schema_version}`  ·  cre: "
        f"`{manifest.get('versions', {}).get('cre', '—')}`",
        f"- id: `{ident.id}`",
        f"- aliases: {', '.join(ident.aliases) if ident.aliases else '—'}",
        "",
        "## Fuentes utilizadas",
        f"- proveedores disponibles: {', '.join(available) if available else '—'}",
        f"- proveedores preparados (sin datos): {', '.join(pending) if pending else '—'}",
        "- referencias / URLs: "
        + (", ".join(bible.sources) if bible.sources else "—"),
        "",
        "## Identity",
        f"- nationality: {_filled(ident.nationality)}",
        f"- birth_date: {_filled(ident.birth_date)}",
        f"- death_date: {_filled(ident.death_date)}",
        f"- occupation: {_filled(ident.occupation)}",
        "",
        "## Biografía",
        f"- summary: {('sí (' + str(len(bible.biography.summary)) + ' car.)') if bible.biography.summary else '—'}",
        f"- cronología (timeline): {_filled(bible.biography.timeline)}",
        f"- eventos importantes: {_filled(bible.biography.important_events)}",
        f"- lugares: {_filled(bible.biography.locations)}",
        f"- relaciones: {_filled(bible.biography.relationships)}",
        "",
        "## Referencias visuales",
        f"- total: {len(bible.visual_references)}",
    ]
    for ref in bible.visual_references[:15]:
        lines.append(
            f"  - `{ref.id or ref.caption}` · {ref.resolution or '?'} · "
            f"licencia: {ref.license or '—'} · {ref.url or '—'}"
        )
    lines += [
        "",
        "## Cobertura de la investigación",
        f"- campos con dato: {len(found)} / {len(found) + len(empty)} "
        f"({coverage:.0f}%)",
        f"- campos vacíos: {', '.join(empty) if empty else '—'}",
        f"- conflictos entre fuentes: {len(bible.conflicts)}",
        "",
        "## Trazabilidad",
        f"- entradas de provenance: {len(bible.provenance)} "
        "(cada dato indica proveedor y confianza)",
    ]
    for conflict in bible.conflicts:
        cand = " | ".join(
            f"{c['value']} ({c['provider']}, {c['confidence']})"
            for c in conflict["candidates"]
        )
        lines.append(f"  - conflicto `{conflict['field']}`: {cand}")
    lines += [
        "",
        "> Los campos sin datos quedan vacíos a propósito (no se inventan). Cada dato "
        "presente es trazable a un proveedor en `provenance`. Las imágenes no se "
        "descargan: solo se catalogan referencias con su licencia.",
        "",
    ]
    return "\n".join(lines)
