"""Persistencia del ERE: escribe los artefactos de evidencia.

- ``evidence_graph.json``    (grafo reproducible, versionado, sin marca temporal)
- ``evidence_manifest.json`` (proveedores, errores, estadísticas, cobertura, tiempos,
                              checksum del grafo y sello temporal)
- ``evidence_report.md``     (resumen legible)

El grafo es reproducible (mismo input → mismo JSON). La marca temporal y el checksum
viven en el manifest, no en el grafo.
"""

import hashlib
import json
import os
import time

from app.ere.models import EvidenceGraph


def _canonical_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def write_outputs(
    out_dir: str, graph: EvidenceGraph, manifest: dict, *, generated_at: float | None = None
) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    graph_path = os.path.join(out_dir, "evidence_graph.json")
    manifest_path = os.path.join(out_dir, "evidence_manifest.json")
    report_path = os.path.join(out_dir, "evidence_report.md")

    graph_json = _canonical_json(graph.to_dict())
    with open(graph_path, "w", encoding="utf-8") as handle:
        handle.write(graph_json)

    manifest_out = dict(manifest)
    manifest_out["graph_checksum"] = (
        "sha256:" + hashlib.sha256(graph_json.encode("utf-8")).hexdigest()
    )
    manifest_out["generated_at"] = generated_at if generated_at is not None else time.time()
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest_out, handle, ensure_ascii=False, indent=2)

    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(_render_report(graph, manifest_out))

    return {"graph": graph_path, "manifest": manifest_path, "report": report_path}


def _render_report(graph: EvidenceGraph, manifest: dict) -> str:
    stats = manifest.get("statistics", {})
    available = [p["provider"] for p in manifest.get("providers", []) if p.get("available")]
    pending = [p["provider"] for p in manifest.get("providers", []) if not p.get("available")]
    cov = manifest.get("coverage", {})

    lines = [
        f"# Evidence Report — {graph.project.name or '(sin caso)'}",
        "",
        f"- caso: **{graph.project.name}**"
        + (f" · lugar: {graph.project.location}" if graph.project.location else "")
        + (f" · fecha: {graph.project.date}" if graph.project.date else ""),
        f"- schema: `{graph.schema_version}` · ere: "
        f"`{manifest.get('versions', {}).get('ere', '—')}`",
        f"- checksum del grafo: `{manifest.get('graph_checksum', '—')}`",
        "",
        "## Resumen",
        f"- entidades: {stats.get('entities', 0)} · eventos: {stats.get('events', 0)} "
        f"· relaciones: {stats.get('relationships', 0)}",
        f"- noticias: {stats.get('articles', 0)} · imágenes: {stats.get('images', 0)} "
        f"· vídeos: {stats.get('videos', 0)} · judiciales: {stats.get('court_documents', 0)}",
        f"- conflictos: {stats.get('conflicts', 0)} · fuentes: {stats.get('sources', 0)}",
        "",
        "## Fuentes utilizadas",
        f"- proveedores con datos: {', '.join(available) if available else '—'}",
        f"- proveedores preparados (sin datos): {', '.join(pending) if pending else '—'}",
        "",
        "## Cobertura",
        f"- categorías con datos: {cov.get('buckets_with_data', 0)}/"
        f"{cov.get('buckets_total', 0)} ({cov.get('ratio', 0) * 100:.0f}%)",
        "",
        "## Personajes / entidades",
    ]
    for entity in graph.entities:
        attrs = ", ".join(sorted(entity.attributes.keys())) or "—"
        alias = f" (alias: {', '.join(entity.aliases)})" if entity.aliases else ""
        lines.append(
            f"- `{entity.id}` **{entity.canonical_name or '?'}**{alias} · "
            f"atributos: {attrs} · refs: {len(entity.references)}"
        )

    lines += ["", "## Noticias"]
    for art in graph.articles[:20]:
        lines.append(f"- {art.date or '?'} · {art.medium or '?'} · {art.headline} · {art.url}")
    if not graph.articles:
        lines.append("- —")

    lines += ["", "## Imágenes (referencias, sin descarga)"]
    for img in graph.images[:20]:
        lines.append(
            f"- `{img.id}` · {img.resolution or '?'} · licencia: {img.license or '—'} "
            f"· {img.original_url}"
        )
    if not graph.images:
        lines.append("- —")

    lines += ["", "## Vídeos (metadatos)"]
    for vid in graph.videos[:20]:
        lines.append(f"- `{vid.id}` · {vid.title} · {vid.channel or '?'} · {vid.url}")
    if not graph.videos:
        lines.append("- —")

    lines += ["", "## Conflictos (no resueltos, se conservan ambos)"]
    for conflict in graph.conflicts:
        cand = " | ".join(
            f"{c['value']} ({c['provider']}, {c['confidence']})" for c in conflict["candidates"]
        )
        lines.append(f"- `{conflict['entity_id']}` / {conflict['field']}: {cand}")
    if not graph.conflicts:
        lines.append("- —")

    lines += ["", "## Licencias de las fuentes"]
    licenses = sorted({s.license for s in graph.sources if s.license})
    lines.append("- " + (", ".join(licenses) if licenses else "—"))

    lines += [
        "",
        "## Nivel de confianza",
        "- cada dato lleva proveedor + confianza (ver `provenance` de cada claim y el "
        "manifest). Los desacuerdos se conservan, no se deciden.",
        "",
        "> El ERE no inventa: las categorías sin datos quedan vacías. Las imágenes y "
        "vídeos solo se catalogan (sin descarga). Las referencias judiciales no se "
        "interpretan.",
        "",
    ]
    return "\n".join(lines)
