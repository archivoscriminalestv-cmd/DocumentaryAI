"""Reconstruye la base de estilos a partir de la base de conocimiento del DLE (DKS-001).

    python -m app.cli.synthesize_knowledge
    python -m app.cli.synthesize_knowledge --knowledge knowledge --out knowledge/styles

Lee ``knowledge/documentaries/`` y escribe ``knowledge/styles/*.json``. No descarga ni
analiza vídeo: solo sintetiza. Reproducible.
"""

import argparse
import os
import sys

from app.dks.loader import load_corpus
from app.dks.persistence import write_styles
from app.dks.synthesizer import KnowledgeSynthesizer


def run(knowledge_root: str = "knowledge", out_dir: str | None = None) -> dict:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    out_dir = out_dir or os.path.join(knowledge_root, "styles")
    corpus = load_corpus(knowledge_root)
    profiles = KnowledgeSynthesizer(corpus).synthesize()
    paths = write_styles(profiles, out_dir)

    print(f"Documentales leídos: {len(corpus)}  ·  planos: {len(corpus.all_shots())}")
    print("Perfiles de estilo escritos:")
    for name, path in paths.items():
        print(f"  {name:24} -> {path}")
    return {"documentaries": len(corpus), "paths": paths}


def main() -> None:
    p = argparse.ArgumentParser(description="Sintetiza la base de estilos (DKS).")
    p.add_argument("--knowledge", default="knowledge", help="raíz de la base de conocimiento")
    p.add_argument("--out", default=None, help="directorio de salida (def. <knowledge>/styles)")
    args = p.parse_args()
    run(args.knowledge, args.out)


if __name__ == "__main__":
    main()
