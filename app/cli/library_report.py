"""Informe y búsqueda de la biblioteca permanente de assets (ALR).

    python -m app.cli.library_report
    python -m app.cli.library_report --search character=Coquito provider=huggingface scene=scene-02

Imprime las estadísticas de ``library/`` y, si se pasan filtros ``--search clave=valor``,
lista los assets que cumplen TODOS los filtros. No genera ni modifica imágenes.
"""

import argparse
import sys

from app.alr import AssetLibrary, search_assets


def run(filters: dict) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    library = AssetLibrary()
    print(library.report())
    library.write_report()

    if filters:
        results = search_assets(library.registry, **filters)
        print(f"\n=== SEARCH {filters} -> {len(results)} assets ===")
        for a in results[:50]:
            print(f"  {a.asset_id}  {a.provider}/{a.model}  {a.resolution}  "
                  f"refs={a.reference_count}  scene={a.scene}  char={a.character_name}")


def _parse_filters(pairs: list[str]) -> dict:
    out = {}
    for pair in pairs or []:
        if "=" in pair:
            key, value = pair.split("=", 1)
            out[key.strip()] = value.strip()
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="ALR library report & search.")
    parser.add_argument("--search", nargs="*", default=[], metavar="key=value",
                        help="Filtros de búsqueda (p.ej. character=Coquito provider=huggingface)")
    args = parser.parse_args()
    run(_parse_filters(args.search))


if __name__ == "__main__":
    main()
