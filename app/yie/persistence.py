"""Persistencia del YIE: escribe el conocimiento de YouTube por documental.

En ``knowledge/documentaries/<doc_id>/``:
    youtube.json · seo.json · thumbnail.json · popularity.json

No se mezcla con los JSON del DLE (cada subsistema mantiene sus propios ficheros).
Reproducible (``sort_keys``, sin marcas de tiempo ocultas).
"""

import json
import os


def _dump(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def write_intelligence(doc_dir: str, youtube, seo, thumbnail, popularity) -> dict[str, str]:
    os.makedirs(doc_dir, exist_ok=True)
    paths = {
        "youtube": os.path.join(doc_dir, "youtube.json"),
        "seo": os.path.join(doc_dir, "seo.json"),
        "thumbnail": os.path.join(doc_dir, "thumbnail.json"),
        "popularity": os.path.join(doc_dir, "popularity.json"),
    }
    _dump(paths["youtube"], youtube.to_dict())
    _dump(paths["seo"], seo.to_dict())
    _dump(paths["thumbnail"], thumbnail.to_dict())
    _dump(paths["popularity"], popularity.to_dict())
    return paths
