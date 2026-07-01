"""Carga de conocimiento para el Production Context (PCX).

Convierte un ``GenerationKnowledge`` (del KBG, como objeto o como dict de su JSON) en
decisiones NEUTRALES, **ignorando las UNKNOWN**. Tolera artefactos inexistentes (devuelve
``None``/vacío). Nunca inventa.
"""

import json
import os

from app.pcx import UNKNOWN
from app.pcx.models import DecisionView


def _field(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def decisions_from_generation_knowledge(gk) -> dict[str, dict[str, DecisionView]]:
    """gk: objeto ``GenerationKnowledge`` del KBG o su ``to_dict()``. Filtra UNKNOWN."""
    out: dict[str, dict[str, DecisionView]] = {}
    if gk is None:
        return out
    sections = _field(gk, "sections", {}) or {}
    for name, decisions in sections.items():
        for d in decisions:
            value = _field(d, "value")
            if value is None or value == UNKNOWN:
                continue                               # UNKNOWN nunca entra al contexto
            key = _field(d, "key")
            if not key:
                continue
            out.setdefault(name, {})[key] = DecisionView(
                value=value,
                confidence=float(_field(d, "confidence", 0.0) or 0.0),
                origin=str(_field(d, "origin", "") or ""))
    return out


def genre_of(gk, default: str = UNKNOWN) -> str:
    return str(_field(gk, "genre", default) or default) if gk is not None else default


def load_generation_knowledge(*, generation_knowledge=None, gk_json_path: str = "",
                              styles_root: str = "", genre: str = "documentary_style",
                              ece_coverage_path: str = ""):
    """Obtiene un GenerationKnowledge tolerando ausencias (devuelve ``None`` si no hay).

    Prioridad: objeto inyectado > JSON en disco > construirlo vía KBG (import perezoso).
    """
    if generation_knowledge is not None:
        return generation_knowledge
    if gk_json_path and os.path.isfile(gk_json_path):
        try:
            with open(gk_json_path, encoding="utf-8") as h:
                return json.load(h)
        except (OSError, json.JSONDecodeError):
            return None
    if styles_root:
        try:
            from app.kbg.bridge import KnowledgeBridge      # import perezoso (PCX→KBG)
            return KnowledgeBridge(styles_root=styles_root).build(
                genre=genre, ece_coverage_path=ece_coverage_path)
        except Exception:
            return None
    return None
