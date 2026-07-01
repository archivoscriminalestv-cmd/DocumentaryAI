"""Persistencia del DocumentaryDossier (ERE-003).

Escribe los artefactos oficiales:
    documentary_dossier.json · documentary_dossier.md · timeline.json ·
    media_catalog.json · people.json · locations.json · manifest.json

El dossier JSON es reproducible (``sort_keys``, sin marca temporal). El manifest lleva
el checksum y el sello temporal.
"""

import hashlib
import json
import os
import time
from dataclasses import asdict

from app.dossier import DOSSIER_VERSION
from app.dossier.models import DocumentaryDossier


def _dump(path: str, data, *, sort_keys: bool = True) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=sort_keys)


def write_outputs(
    out_dir: str, dossier: DocumentaryDossier, *, evidence_manifest: dict | None = None,
    generated_at: float | None = None,
) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    paths = {
        "dossier": os.path.join(out_dir, "documentary_dossier.json"),
        "report": os.path.join(out_dir, "documentary_dossier.md"),
        "timeline": os.path.join(out_dir, "timeline.json"),
        "media": os.path.join(out_dir, "media_catalog.json"),
        "people": os.path.join(out_dir, "people.json"),
        "locations": os.path.join(out_dir, "locations.json"),
        "manifest": os.path.join(out_dir, "manifest.json"),
    }

    dossier_dict = dossier.to_dict()
    dossier_json = json.dumps(dossier_dict, ensure_ascii=False, indent=2, sort_keys=True)
    with open(paths["dossier"], "w", encoding="utf-8") as handle:
        handle.write(dossier_json)

    _dump(paths["timeline"], [asdict(e) for e in dossier.timeline])
    _dump(paths["media"], {
        "images": [asdict(m) for m in dossier.media_images],
        "videos": [asdict(m) for m in dossier.media_videos],
    })
    _dump(paths["people"], [asdict(p) for p in dossier.people])
    _dump(paths["locations"], [asdict(loc) for loc in dossier.locations])

    manifest = {
        "schema_version": dossier.schema_version,
        "versions": {"schema": dossier.schema_version, "dossier": DOSSIER_VERSION},
        "project": dossier.project,
        "providers_used": dossier.providers_used,
        "statistics": {
            "people": len(dossier.people),
            "timeline_events": len(dossier.timeline),
            "locations": len(dossier.locations),
            "images": len(dossier.media_images),
            "videos": len(dossier.media_videos),
            "news": len(dossier.news),
            "court_documents": len(dossier.court_documents),
            "relationships": len(dossier.relationships),
            "conflicts": len(dossier.conflicts),
            "sources": len(dossier.sources),
        },
        "coverage": dossier.coverage,
        "dossier_checksum": "sha256:" + hashlib.sha256(dossier_json.encode("utf-8")).hexdigest(),
        "generated_at": generated_at if generated_at is not None else time.time(),
    }
    if evidence_manifest is not None:
        manifest["evidence"] = evidence_manifest
    _dump(paths["manifest"], manifest, sort_keys=False)

    with open(paths["report"], "w", encoding="utf-8") as handle:
        handle.write(_render_report(dossier, manifest))

    return paths


def _claim_line(claims) -> str:
    parts = []
    for c in claims:
        parts.append(f"{c.value} (conf {c.confidence}, {c.provider or '?'}"
                     + (f", {c.license}" if c.license else "") + ")")
    return " | ".join(parts) if parts else "—"


def _render_report(dossier: DocumentaryDossier, manifest: dict) -> str:
    stats = manifest["statistics"]
    cov = manifest["coverage"]
    project = dossier.project

    lines = [
        f"# Documentary Dossier — {project.get('title') or project.get('canonical_name') or '(sin caso)'}",
        "",
        f"- sujeto: **{project.get('canonical_name') or '?'}** "
        f"(`{project.get('subject_id', '')}`)",
        f"- versión: `{manifest['versions']['dossier']}` · checksum: "
        f"`{manifest['dossier_checksum']}`",
        "",
        "## Resumen",
        f"- personas: {stats['people']} · eventos: {stats['timeline_events']} · "
        f"lugares: {stats['locations']} · relaciones: {stats['relationships']}",
        f"- noticias: {stats['news']} · imágenes: {stats['images']} · "
        f"vídeos: {stats['videos']} · judiciales: {stats['court_documents']}",
        f"- conflictos: {stats['conflicts']} · fuentes: {stats['sources']}",
        "",
        "## Cronología",
    ]
    for event in dossier.timeline:
        lines.append(
            f"- {event.date or '¿fecha?'}{(' ' + event.time) if event.time else ''} · "
            f"{event.description or '—'} (conf {event.confidence}, {event.provider or '?'})"
        )
    if not dossier.timeline:
        lines.append("- —")

    lines += ["", "## Personajes"]
    for person in dossier.people:
        lines.append(f"### {person.name or person.id}")
        if person.aliases:
            lines.append(f"- alias: {', '.join(person.aliases)}")
        for field_name, claims in sorted(person.attributes.items()):
            lines.append(f"- {field_name}: {_claim_line(claims)}")
        if person.family:
            lines.append(f"- familia: {_claim_line(person.family)}")
        if person.organizations:
            lines.append(f"- organizaciones: {_claim_line(person.organizations)}")
        lines.append(f"- fotos: {len(person.photos)} · vídeos: {len(person.videos)} · "
                     f"lugares habituales: {len(person.usual_locations)}")
    if not dossier.people:
        lines.append("- —")

    lines += ["", "## Lugares"]
    for loc in dossier.locations:
        lines.append(f"- `{loc.id}` {loc.name} [{loc.type}] · coords: "
                     f"{loc.coordinates or '—'} · ({loc.provider or '?'})")
    if not dossier.locations:
        lines.append("- —")

    lines += ["", "## Material audiovisual (referencias, sin descarga)"]
    for img in dossier.media_images[:30]:
        lines.append(f"- IMG `{img.id}` · {img.resolution or '?'} · "
                     f"licencia: {img.license or '—'} · {img.url}")
    for vid in dossier.media_videos[:30]:
        lines.append(f"- VID `{vid.id}` · {vid.title} · {vid.url}")
    if not (dossier.media_images or dossier.media_videos):
        lines.append("- —")

    lines += ["", "## Fuentes"]
    for src in dossier.sources:
        lines.append(f"- {src.provider or '?'} · {src.url or '—'} · "
                     f"licencia: {src.license or '—'} · conf {src.confidence}")
    if not dossier.sources:
        lines.append("- —")

    lines += ["", "## Conflictos (no resueltos, se conservan todos)"]
    for c in dossier.conflicts:
        cand = " | ".join(f"{x['value']} ({x['provider']}, {x['confidence']})"
                          for x in c.candidates)
        lines.append(f"- [{c.type}] `{c.subject}` / {c.field}: {cand}")
    if not dossier.conflicts:
        lines.append("- —")

    lines += [
        "",
        "## Cobertura y calidad",
        f"- categorías con datos: {cov['buckets_with_data']}/{cov['buckets_total']} "
        f"({cov['ratio'] * 100:.0f}%)",
        f"- afirmaciones puntuadas: {cov['facts_scored']} · "
        f"confianza media: {cov['average_confidence']}",
        "",
        "> Solo información pública y verificable. Cada afirmación conserva confianza, "
        "proveedor, fuente y licencia. Sin resúmenes, narrativa, prompts ni decisiones "
        "sobre relevancia: eso corresponde al Director IA posteriormente.",
        "",
    ]
    return "\n".join(lines)
