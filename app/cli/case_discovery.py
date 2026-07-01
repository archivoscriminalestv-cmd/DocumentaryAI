"""Case Discovery (EAE-003): planifica y DESCUBRE el material de un caso (sin descargar).

    python -m app.cli.case_discovery --case-id case_madeleine --title "..." \
        --genre true_crime --subject "..." --person "..." --location "..." --event "..."
    python -m app.cli.case_discovery --profile profile.json
    python -m app.cli.case_discovery --plan plan.json

Lee/crea un InvestigationPlan, ejecuta el Discovery, crea el Workspace y escribe
manifest.json · sources.json · timeline.json · verification.json · report.json ·
discovery_report.md  en  output/projects/<case>/.  NO descarga binarios.
"""

import argparse
import json
import os
import sys

from app.eae.discovery.cache import DiscoveryCache
from app.eae.discovery.engine import CaseDiscoveryEngine
from app.eae.discovery.http import RealHttpClient
from app.eae.discovery.manifest import build_manifest
from app.eae.discovery.persistence import write_outputs
from app.eae.discovery.registry import default_registry
from app.eae.planner import CaseProfile, EvidenceInvestigationPlanner, InvestigationPlan
from app.eae.workspace import WorkspaceManager


def _load_plan(args) -> InvestigationPlan:
    if args.plan:
        with open(args.plan, encoding="utf-8") as h:
            return InvestigationPlan.from_dict(json.load(h))
    if args.profile:
        with open(args.profile, encoding="utf-8") as h:
            profile = CaseProfile.from_dict(json.load(h))
    else:
        profile = CaseProfile(
            case_id=args.case_id, title=args.title, genre=args.genre, subject=args.subject,
            people=args.person, locations=args.location, events=args.event,
            license_requirements=args.license)
    return EvidenceInvestigationPlanner().plan(profile)


def run(args, *, registry=None) -> dict:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    lang = getattr(args, "lang", "en")
    plan = _load_plan(args)
    if registry is None:
        # Producción: clientes reales (en sandbox sin red, degrada a UNKNOWN sin romper).
        http = None if getattr(args, "offline", False) else RealHttpClient()
        registry = default_registry(http=http, cache=DiscoveryCache())
    discovery_plan = CaseDiscoveryEngine(registry=registry, language=lang).discover(plan)
    manifest = build_manifest(plan, discovery_plan)

    ws = WorkspaceManager(args.output_dir).create(plan.case_id)
    paths = write_outputs(ws, plan, discovery_plan, manifest, registry)

    # Correlación (ECE): grafo + cobertura + conflictos + candidatos de recreación.
    from app.ece.engine import CaseCorrelationEngine
    from app.ece.persistence import write_correlation_outputs
    correlation = CaseCorrelationEngine().analyze(plan, discovery_plan)
    paths.update(write_correlation_outputs(ws.project_dir, correlation))

    t = discovery_plan.totals
    print(f"CASE: {discovery_plan.title or plan.case_id} ({plan.case_id})")
    print(f"Necesidades: {t['needs']}  (mínimo de evidencias: {t['required']})")
    print("\nMaterial localizado:")
    if discovery_plan.by_provider:
        for provider, count in discovery_plan.by_provider.items():
            print(f"  {provider:20} {count}")
    else:
        print("  — (proveedores en modo contrato: sin cliente HTTP / sin red)")
    print("\nCobertura:")
    for category, agg in discovery_plan.by_category.items():
        print(f"  {category:18} {agg.get('state', '—')}  "
              f"({agg['discovered']}/{agg['required']})")
    cov = correlation.coverage.summary
    print("\nCorrelación (ECE):")
    print(f"  grafo: {len(correlation.graph.nodes)} nodos · "
          f"{len(correlation.graph.relations)} relaciones")
    print(f"  cobertura: {cov.get('complete', 0)} COMPLETE · {cov.get('partial', 0)} PARTIAL "
          f"· {cov.get('missing', 0)} MISSING")
    print(f"  conflictos: {len(correlation.conflicts)} (requieren verificación) · "
          f"candidatos de recreación: {len(correlation.recreation_candidates)}")

    print(f"\nWorkspace creado: {ws.workspace_dir}")
    print("No se ha descargado ningún binario.")
    return {"plan": plan, "discovery": discovery_plan, "correlation": correlation,
            "paths": paths, "workspace": ws}


def main() -> None:
    p = argparse.ArgumentParser(description="Case Discovery Engine (EAE-003).")
    p.add_argument("--case-id", default="case")
    p.add_argument("--title", default="")
    p.add_argument("--genre", default="generic")
    p.add_argument("--subject", default="")
    p.add_argument("--person", action="append", default=[])
    p.add_argument("--location", action="append", default=[])
    p.add_argument("--event", action="append", default=[])
    p.add_argument("--license", action="append", default=[])
    p.add_argument("--profile", default=None, help="ruta a un CaseProfile JSON")
    p.add_argument("--plan", default=None, help="ruta a un InvestigationPlan JSON")
    p.add_argument("--lang", default="en", help="idioma de las fuentes (def. 'en')")
    p.add_argument("--offline", action="store_true",
                   help="no usar red (proveedores como contrato)")
    p.add_argument("--output-dir", default=os.path.join("output", "projects"))
    args = p.parse_args()
    run(args)


if __name__ == "__main__":
    main()
