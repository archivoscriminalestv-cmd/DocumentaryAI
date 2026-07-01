"""CLI del Project Knowledge Loader (ERE-002).

Construye el contexto documental oficial del ERE:

    python -m app.cli.project_knowledge --title "Coquito" \
        --canonical-name "Jonathan Burgos" --alias "Coquito" \
        --location "Trinitat Vella" --location "Barcelona" --date "2021-01-04" \
        --genre true_crime --keyword "asesinato" --keyword "Mossos"

Genera ``output/project/project_knowledge.json`` (entrada oficial del ERE).
"""

import argparse
import os
import sys

from app.ere.project_knowledge import ProjectKnowledge


def main(argv: list[str] | None = None) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Project Knowledge Loader (ERE).")
    parser.add_argument("--title", required=True, help="Título del proyecto/caso.")
    parser.add_argument("--canonical-name", default="", help="Nombre real del sujeto.")
    parser.add_argument("--alias", action="append", default=[], help="Alias (repetible).")
    parser.add_argument("--person", action="append", default=[], help="Persona conocida (repetible).")
    parser.add_argument("--location", action="append", default=[], help="Ubicación (repetible).")
    parser.add_argument("--date", action="append", default=[], help="Fecha (repetible).")
    parser.add_argument("--country", default="", help="País.")
    parser.add_argument("--language", default="", help="Idioma (p.ej. 'es').")
    parser.add_argument("--genre", default="", help="Género (p.ej. true_crime).")
    parser.add_argument("--keyword", action="append", default=[], help="Palabra clave (repetible).")
    parser.add_argument("--type", dest="documentary_type", default="", help="Tipo documental.")
    parser.add_argument("--notes", default="", help="Notas libres.")
    parser.add_argument(
        "--output-dir", default=os.path.join("output", "project"),
        help="Directorio de salida.",
    )
    args = parser.parse_args(argv)

    knowledge = ProjectKnowledge(
        title=args.title, canonical_name=args.canonical_name, aliases=args.alias,
        known_people=args.person, locations=args.location, dates=args.date,
        country=args.country, language=args.language, genre=args.genre,
        keywords=args.keyword, documentary_type=args.documentary_type, notes=args.notes,
    )
    os.makedirs(args.output_dir, exist_ok=True)
    path = os.path.join(args.output_dir, "project_knowledge.json")
    knowledge.save(path)

    print(f"ProjectKnowledge: {knowledge.title} (sujeto: {knowledge.subject_name()})")
    print(f"  aliases: {', '.join(knowledge.aliases) or '—'}")
    print(f"  locations: {', '.join(knowledge.locations) or '—'} · dates: "
          f"{', '.join(knowledge.dates) or '—'}")
    print(f"  keywords: {', '.join(knowledge.keywords) or '—'}")
    print(f"  -> {path}")


if __name__ == "__main__":
    main()
