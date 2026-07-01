"""Persistencia del descubrimiento (EAE-003) — escribe metadatos del proyecto (sin binarios).

En ``output/projects/<case>/``: manifest.json, sources.json, timeline.json,
verification.json, report.json y discovery_report.md. Reproducible (``sort_keys``).
"""

import json
import os

from app.eae.models import VerificationStatus


def _dump(path: str, payload) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def write_outputs(workspace, plan, discovery_plan, manifest, registry) -> dict[str, str]:
    os.makedirs(workspace.project_dir, exist_ok=True)
    paths = {name: workspace.metadata_path(name) for name in (
        "manifest.json", "sources.json", "timeline.json", "verification.json",
        "report.json", "discovery_report.md")}

    _dump(paths["manifest.json"], manifest.to_dict())
    _dump(paths["sources.json"], {
        "providers": registry.capabilities(),
        "consulted": list(discovery_plan.sources_consulted),
    })
    _dump(paths["timeline.json"], {
        "events": list(plan.profile.events if plan.profile else []),
        "people": list(plan.profile.people if plan.profile else []),
        "locations": list(plan.profile.locations if plan.profile else []),
    })
    _dump(paths["verification.json"], {
        "entries": [{"evidence_id": e.evidence_id, "status": VerificationStatus.UNVERIFIED,
                     "validated": False} for e in manifest.entries],
    })
    _dump(paths["report.json"], discovery_plan.to_dict())

    with open(paths["discovery_report.md"], "w", encoding="utf-8") as handle:
        handle.write(_render_report(workspace, plan, discovery_plan))
    return paths


def _render_report(workspace, plan, discovery_plan) -> str:
    t = discovery_plan.totals
    lines = [
        f"# Discovery report — {discovery_plan.title or discovery_plan.case_id}",
        "",
        f"- caso: `{discovery_plan.case_id}`",
        f"- Para producir este documental necesito **{t.get('required', 0)} evidencias** "
        f"(mínimos del plan, {t.get('needs', 0)} necesidades).",
        f"- He localizado: **{t.get('discovered', 0)}**  ·  pendientes: "
        f"**{t.get('pending', 0)}**.",
        "",
        "## Material localizado por proveedor",
    ]
    for provider, count in (discovery_plan.by_provider or {}).items():
        ms = discovery_plan.timings.get(provider, 0.0)
        lines.append(f"- **{provider}**: {count} ({ms} ms)")
    if not discovery_plan.by_provider:
        lines.append("- — (proveedores en modo contrato: sin cliente HTTP)")
    lines += ["", "## Cobertura por categoría"]
    for category, agg in discovery_plan.by_category.items():
        sources = ", ".join(agg["candidate_providers"]) or "—"
        lines.append(
            f"- **{category}**: {agg.get('state', '—')} "
            f"{agg['discovered']}/{agg['required']} (pendientes {agg['pending']}) "
            f"· fuentes candidatas: {sources}")
    lines += ["", "## Necesidades pendientes"]
    pending = [n for n in discovery_plan.needs if n.discovered < n.minimum]
    for n in pending:
        lines.append(f"- `{n.need_id}` [{n.priority}] {n.category}/{n.target} "
                     f"· faltan {max(0, n.minimum - n.discovered)}")
    if not pending:
        lines.append("- —")
    lines += [
        "",
        "## Fuentes consultadas",
        "- " + (", ".join(discovery_plan.sources_consulted) or "ninguna disponible (contratos)"),
        "",
        "## Workspace temporal",
        f"- `{workspace.workspace_dir}` (downloads/photos/videos/documents/audio/maps/news/cache)",
        "",
        "> No se ha descargado ningún binario. Solo permanecerán metadatos, hashes, URLs, "
        "licencias, referencias y conocimiento; los binarios del workspace se eliminan al "
        "finalizar el proyecto.",
        "",
    ]
    return "\n".join(lines)
