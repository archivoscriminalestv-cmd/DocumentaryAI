"""ReferenceLibrary — almacén del conocimiento reutilizable del RDA.

Cada ``CinematicProfile`` se guarda como JSON. La biblioteca acumula gramáticas
de varias referencias; es la base de conocimiento que ALIMENTA ARCH-VIS-000 y el
futuro VIS (calibración de umbrales, presets de estilo, etc.). No guarda ningún
contenido del vídeo original, solo estadísticas.
"""

import json
import os
import re
from dataclasses import asdict

from app.rda.models import CinematicProfile


def _slug(text: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", os.path.basename(text).lower()).strip("-")
    return (base or "reference")[:60]


class ReferenceLibrary:
    def __init__(self, base_dir: str = os.path.join("output", "rda")) -> None:
        self._dir = base_dir
        os.makedirs(self._dir, exist_ok=True)

    @property
    def base_dir(self) -> str:
        return self._dir

    def save(self, profile: CinematicProfile) -> str:
        name = f"{_slug(profile.reference)}.json"
        path = os.path.join(self._dir, name)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(asdict(profile), handle, ensure_ascii=False, indent=2)
        return path

    def list_profiles(self) -> list[str]:
        return sorted(
            os.path.join(self._dir, f) for f in os.listdir(self._dir) if f.endswith(".json")
        )

    def load(self, path: str) -> dict:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
