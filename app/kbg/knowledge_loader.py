"""Carga de conocimiento PÚBLICO para el KBG.

Lee únicamente artefactos públicos en disco (knowledge/styles/, output/advisor/,
output/dca/, output/ece/…). Nunca accede a estado interno de ningún motor. Determinista:
ordena y, si falta un fichero, devuelve ``None`` (UNKNOWN antes que inventar).
"""

import json
import os
from dataclasses import dataclass, field


@dataclass
class KnowledgeBundle:
    styles_root: str
    styles: dict = field(default_factory=dict)       # nombre -> contenido del perfil
    sources: dict = field(default_factory=dict)      # nombre -> ruta relativa
    extra: dict = field(default_factory=dict)         # advisor/dca/ece opcionales

    def style(self, name: str):
        return self.styles.get(name)

    def source(self, name: str) -> str:
        return self.sources.get(name, "")


def _read_json(path: str):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


def load_styles(styles_root: str = os.path.join("knowledge", "styles")) -> KnowledgeBundle:
    bundle = KnowledgeBundle(styles_root=styles_root)
    if os.path.isdir(styles_root):
        for fname in sorted(os.listdir(styles_root)):
            if not fname.endswith(".json"):
                continue
            data = _read_json(os.path.join(styles_root, fname))
            if isinstance(data, dict):
                name = fname[:-5]
                bundle.styles[name] = data
                bundle.sources[name] = os.path.join(styles_root, fname)
    return bundle


def load_optional(bundle: KnowledgeBundle, *, ece_coverage: str = "") -> KnowledgeBundle:
    """Carga artefactos opcionales (p.ej. un coverage_report.json del ECE)."""
    if ece_coverage and os.path.isfile(ece_coverage):
        data = _read_json(ece_coverage)
        if isinstance(data, dict):
            bundle.extra["ece_coverage"] = data
            bundle.sources["ece_coverage"] = ece_coverage
    return bundle
