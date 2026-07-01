"""Single command: analiza un vídeo de referencia y guarda su gramática visual.

    python -m app.cli.analyze_reference "<youtube-url | ruta-mp4>"

Extrae SOLO la gramática audiovisual (no contenido), la guarda en la biblioteca
de referencias (output/rda/) e imprime el CinematicProfile + las notas de
gramática que alimentarán ARCH-VIS-000 y el VIS.
"""

import json
import sys
from dataclasses import asdict

from app.rda.analyzer import ReferenceDocumentaryAnalyzer
from app.rda.library import ReferenceLibrary
from app.rda.sources import RDASourceError


def run(reference: str) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    library = ReferenceLibrary()
    analyzer = ReferenceDocumentaryAnalyzer(library=library)
    try:
        profile = analyzer.analyze(reference)
    except RDASourceError as exc:
        print(f"[RDA] No se pudo obtener la referencia: {exc}")
        raise SystemExit(1)

    data = asdict(profile)
    data.pop("shots", None)  # resumen: omitimos el detalle por plano en consola
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print("\n=== Grammar notes ===")
    for note in profile.grammar_notes:
        print(" -", note)
    print(f"\nPerfil guardado en: {library.save(profile)}")


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    reference = " ".join(args).strip()
    if not reference:
        print('Uso: python -m app.cli.analyze_reference "<youtube-url | ruta-mp4>"')
        raise SystemExit(2)
    run(reference)


if __name__ == "__main__":
    main()
