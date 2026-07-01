"""Contrato de persistencia del VUE (VUE-001).

Define el formato permanente y reproducible del análisis visual. En este sprint NO se
escribe nada en ``knowledge/``: el writer por defecto apunta a ``output/vue/`` y se
ofrece solo para validar el contrato. Reproducible (``sort_keys``, sin marcas de tiempo
añadidas; el timestamp del fotograma forma parte del hecho, no del momento de escritura).
"""

import json
import os

from app.vue import SCHEMA_VERSION
from app.vue.models import VisualAnalysis


def to_payload(analyses: list[VisualAnalysis], *, source: str = "") -> dict:
    """Contrato serializable de un conjunto de análisis de fotogramas."""
    return {
        "schema_version": SCHEMA_VERSION,
        "source": source,
        "frames": [a.to_dict() for a in analyses],
    }


def from_payload(payload: dict) -> list[VisualAnalysis]:
    return [VisualAnalysis.from_dict(f) for f in payload.get("frames", [])]


class VisualAnalysisWriter:
    """Escritor del contrato. NUNCA escribe en knowledge/ (por defecto output/vue/)."""

    def __init__(self, out_dir: str = os.path.join("output", "vue")) -> None:
        if "knowledge" in os.path.normpath(out_dir).split(os.sep):
            raise ValueError("El VUE nunca debe escribir dentro de knowledge/")
        self.out_dir = out_dir

    def write(self, analyses: list[VisualAnalysis], *, name: str = "visual_analysis.json",
              source: str = "") -> str:
        os.makedirs(self.out_dir, exist_ok=True)
        path = os.path.join(self.out_dir, name)
        with open(path, "w", encoding="utf-8") as h:
            json.dump(to_payload(analyses, source=source), h,
                      ensure_ascii=False, indent=2, sort_keys=True)
        return path
