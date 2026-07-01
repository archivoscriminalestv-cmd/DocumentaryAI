"""ResearchNormalizer — fusiona ResearchResult[] en una CharacterBible (CRE).

Fusión DETERMINISTA y TRAZABLE (misma entrada → misma salida):
- escalares: gana el valor de mayor ``confidence``; a igualdad, el primero en el
  orden de los proveedores (compatibilidad "primer no vacío gana"),
- listas: concatenación con deduplicado preservando el orden de aparición,
- visual_references / sources / providers_used: acumulados y deduplicados.

Trazabilidad (CRE-002):
- ``provenance``: de qué proveedor procede cada dato escogido (con su confianza).
- ``conflicts``: cuando varias fuentes discrepan en un escalar, se guardan TODOS
  los candidatos (valor + proveedor + confianza) sin fusionar arbitrariamente.

No inventa datos: solo combina lo que los proveedores aportan. ``canonical_name``,
``id`` y ``aliases`` caen al request (origen ``request``) si nadie los aporta.
"""

from dataclasses import fields

from app.cre.models import (
    Behaviour,
    Biography,
    CharacterBible,
    CharacterRequest,
    Environment,
    Identity,
    PhysicalAppearance,
    Voice,
    slugify,
)
from app.cre.providers.base import ResearchResult

_SECTIONS = {
    "identity": Identity,
    "biography": Biography,
    "physical_appearance": PhysicalAppearance,
    "behaviour": Behaviour,
    "voice": Voice,
    "environment": Environment,
}


def _dedupe(seq: list) -> list:
    seen: list = []
    for item in seq:
        if item not in seen:
            seen.append(item)
    return seen


def _is_empty(value) -> bool:
    return value is None or value == "" or value == []


class ResearchNormalizer:
    def normalize(
        self, request: CharacterRequest, results: list[ResearchResult]
    ) -> CharacterBible:
        available = [r for r in results if r.available]

        merged: dict[str, dict] = {name: {} for name in _SECTIONS}
        # bookkeeping del escalar escogido por campo: {(section, field): conf}
        chosen_conf: dict[tuple, float] = {}
        # candidatos de escalares para detectar conflictos
        candidates: dict[str, list[tuple]] = {}
        provenance: list[dict] = []

        for result in available:
            conf = float(result.confidence)
            for section_name, payload in (result.data or {}).items():
                if section_name not in _SECTIONS or not isinstance(payload, dict):
                    continue
                valid = {f.name for f in fields(_SECTIONS[section_name])}
                for key, value in payload.items():
                    if key not in valid or _is_empty(value):
                        continue
                    path = f"{section_name}.{key}"
                    if isinstance(value, list):
                        bucket = merged[section_name].setdefault(key, [])
                        for item in value:
                            if item not in bucket:
                                bucket.append(item)
                                provenance.append(_prov(path, item, result.provider, conf))
                    else:
                        candidates.setdefault(path, []).append(
                            (value, result.provider, conf)
                        )
                        ck = (section_name, key)
                        if ck not in chosen_conf or conf > chosen_conf[ck]:
                            merged[section_name][key] = value
                            chosen_conf[ck] = conf

        # provenance de los escalares finalmente escogidos
        for (section_name, key), conf in chosen_conf.items():
            value = merged[section_name][key]
            provider = next(
                p for v, p, c in candidates[f"{section_name}.{key}"]
                if v == value and c == conf
            )
            provenance.append(_prov(f"{section_name}.{key}", value, provider, conf))

        conflicts = _conflicts(candidates)

        bible = CharacterBible(
            identity=Identity(**merged["identity"]),
            biography=Biography(**merged["biography"]),
            physical_appearance=PhysicalAppearance(**merged["physical_appearance"]),
            behaviour=Behaviour(**merged["behaviour"]),
            voice=Voice(**merged["voice"]),
            environment=Environment(**merged["environment"]),
            visual_references=_dedupe(
                [vr for r in available for vr in r.visual_references]
            ),
            sources=_dedupe([s for r in available for s in r.sources]),
            providers_used=_dedupe([r.provider for r in available]),
        )

        # Fallbacks de identidad desde el request (origen explícito 'request').
        if not bible.identity.canonical_name:
            bible.identity.canonical_name = request.name
            provenance.append(_prov("identity.canonical_name", request.name, "request", 1.0))
        if not bible.identity.id:
            bible.identity.id = slugify(bible.identity.canonical_name)
            provenance.append(_prov("identity.id", bible.identity.id, "request", 1.0))
        if not bible.identity.aliases and request.aliases:
            bible.identity.aliases = list(request.aliases)
            for alias in request.aliases:
                provenance.append(_prov("identity.aliases", alias, "request", 1.0))

        bible.provenance = sorted(
            provenance, key=lambda p: (p["field"], -p["confidence"], p["provider"], str(p["value"]))
        )
        bible.conflicts = conflicts
        return bible


def _prov(field_path: str, value, provider: str, confidence: float) -> dict:
    return {"field": field_path, "value": value, "provider": provider, "confidence": confidence}


def _conflicts(candidates: dict[str, list[tuple]]) -> list[dict]:
    conflicts: list[dict] = []
    for path in sorted(candidates):
        distinct: list[tuple] = []
        for value, provider, conf in candidates[path]:
            if value not in [d[0] for d in distinct]:
                distinct.append((value, provider, conf))
        if len(distinct) > 1:
            conflicts.append(
                {
                    "field": path,
                    "candidates": [
                        {"value": v, "provider": p, "confidence": c}
                        for v, p, c in distinct
                    ],
                }
            )
    return conflicts
