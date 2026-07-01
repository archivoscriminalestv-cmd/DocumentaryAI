"""CLI del Evidence Research Engine (ERE).

    python -m app.cli.research_evidence --project "Coquito"
    python -m app.cli.research_evidence --project "Coquito" --location "Barcelona" --date "2021-01-04"
    python -m app.cli.research_evidence --project "Coquito" --seed casos/coquito.seed.json
    python -m app.cli.research_evidence --knowledge output/project/project_knowledge.json

Con ``--knowledge`` usa el flujo ERE-002 (Query Builder → Providers → Ranking →
Entity Resolution → Evidence Graph), que prioriza el contexto documental y descarta
resultados irrelevantes por puntuación. Por defecto consulta fuentes reales
(Wikipedia/Wikidata/Commons) + proveedores preparados + mock. Genera en
``output/evidence/<slug>/``:
    evidence_graph.json · evidence_manifest.json · evidence_report.md

Nunca rompe el pipeline: si una fuente falla o no existe, continúa.
"""

import argparse
import os
import sys

from app.ere.models import ProjectQuery, slugify
from app.ere.orchestrator import EvidenceOrchestrator, default_providers, real_providers
from app.ere.project_knowledge import ProjectKnowledge
from app.ere.providers.base import EvidenceProvider


def main(
    argv: list[str] | None = None,
    providers: list[EvidenceProvider] | None = None,
) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Evidence Research Engine (ERE).")
    parser.add_argument("--project", help="Nombre del caso/sujeto (flujo simple).")
    parser.add_argument("--knowledge", default=None,
                        help="Ruta a project_knowledge.json (flujo ERE-002 con ranking).")
    parser.add_argument("--location", default="", help="Ubicación del caso.")
    parser.add_argument("--date", default="", help="Fecha del caso (p.ej. 2021-01-04).")
    parser.add_argument("--alias", action="append", default=[], help="Alias (repetible).")
    parser.add_argument("--lang", default="en", help="Idioma de las fuentes (def. 'en').")
    parser.add_argument("--seed", default=None, help="Ruta a JSON de evidencia curada.")
    parser.add_argument("--min-score", type=float, default=0.15,
                        help="Umbral de ranking para descartar irrelevantes (ERE-002).")
    parser.add_argument(
        "--offline", action="store_true",
        help="Solo catálogo determinista (stubs + mock), sin red.",
    )
    parser.add_argument(
        "--output-dir", default=os.path.join("output", "evidence"),
        help="Directorio base de salida.",
    )
    args = parser.parse_args(argv)

    if not args.project and not args.knowledge:
        parser.error("se requiere --project o --knowledge")

    knowledge = ProjectKnowledge.load(args.knowledge) if args.knowledge else None
    lang = args.lang
    if knowledge and knowledge.language:
        lang = knowledge.language

    if providers is None:
        if args.offline:
            providers = default_providers()
        else:
            providers = real_providers(lang=lang, seed=args.seed)

    orchestrator = EvidenceOrchestrator(providers)
    if knowledge is not None:
        graph, manifest = orchestrator.research_project(knowledge, min_score=args.min_score)
        slug = knowledge.slug()
    else:
        query = ProjectQuery(
            name=args.project, location=args.location, date=args.date, aliases=args.alias
        )
        graph, manifest = orchestrator.research(query)
        slug = slugify(args.project)

    from app.ere.persistence import write_outputs

    out_dir = os.path.join(args.output_dir, slug)
    paths = write_outputs(out_dir, graph, manifest)

    stats = manifest["statistics"]
    available = [p["provider"] for p in manifest["providers"] if p["available"]]
    print(f"Caso: {graph.project.name} (subject={graph.project.subject_id()})")
    print(f"Fuentes con datos: {', '.join(available) or '—'}")
    print(
        f"Entidades: {stats['entities']} · noticias: {stats['articles']} · "
        f"imágenes: {stats['images']} · vídeos: {stats['videos']} · "
        f"relaciones: {stats['relationships']} · conflictos: {stats['conflicts']}"
    )
    if "ranking" in manifest:
        rk = manifest["ranking"]
        qb = manifest["query_builder"]
        print(f"Consultas generadas: {qb['total']} · ranking: {rk['accepted']} aceptadas / "
              f"{rk['rejected']} descartadas (umbral {rk['min_score']})")
    print(f"  graph    -> {paths['graph']}")
    print(f"  manifest -> {paths['manifest']}")
    print(f"  report   -> {paths['report']}")


if __name__ == "__main__":
    main()
