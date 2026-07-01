"""CLI del Character Research Engine (CRE).

    python -m app.cli.research_character --name "Coquito"

Por defecto consulta fuentes REALES (Wikipedia, Wikidata, Commons) + mock de
respaldo. Genera en ``output/research/<slug>/``:
    character_bible.json · research_manifest.json · research_report.md

Opciones:
    --alias       alias del personaje (repetible)
    --lang        idioma de las fuentes (por defecto "en")
    --offline     usa solo el catálogo determinista (stubs + mock), sin red
    --output-dir  directorio base de salida
"""

import argparse
import os
import sys

from app.cre.models import CharacterRequest, slugify
from app.cre.orchestrator import (
    ResearchOrchestrator,
    default_providers,
    real_providers,
)
from app.cre.persistence import write_outputs
from app.cre.providers.base import ResearchProvider


def main(
    argv: list[str] | None = None,
    providers: list[ResearchProvider] | None = None,
) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Character Research Engine (CRE).")
    parser.add_argument("--name", required=True, help="Nombre del personaje.")
    parser.add_argument("--alias", action="append", default=[], help="Alias (repetible).")
    parser.add_argument("--lang", default="en", help="Idioma de las fuentes (def. 'en').")
    parser.add_argument(
        "--offline", action="store_true",
        help="Solo catálogo determinista (stubs + mock), sin red.",
    )
    parser.add_argument(
        "--output-dir", default=os.path.join("output", "research"),
        help="Directorio base de salida.",
    )
    args = parser.parse_args(argv)

    # ``providers`` inyectables (tests). Por defecto: reales, salvo --offline.
    if providers is None:
        providers = default_providers() if args.offline else real_providers(lang=args.lang)

    request = CharacterRequest(name=args.name, aliases=args.alias)
    orchestrator = ResearchOrchestrator(providers)
    bible, manifest = orchestrator.research(request)

    out_dir = os.path.join(args.output_dir, slugify(args.name))
    paths = write_outputs(out_dir, bible, manifest)

    available = [p["provider"] for p in manifest["providers"] if p["available"]]
    print(f"Character: {bible.identity.canonical_name} (id={bible.identity.id})")
    print(f"Fuentes con datos: {', '.join(available) or '—'}")
    print(f"Referencias visuales: {len(bible.visual_references)} · "
          f"conflictos: {len(bible.conflicts)} · provenance: {len(bible.provenance)}")
    print(f"  bible    -> {paths['bible']}")
    print(f"  manifest -> {paths['manifest']}")
    print(f"  report   -> {paths['report']}")


if __name__ == "__main__":
    main()
