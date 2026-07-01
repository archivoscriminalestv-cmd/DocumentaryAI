"""Conflict Engine — detecta incompatibilidades, nunca decide.

Detecta:
- fechas incompatibles (atributos de fecha con >1 valor; eventos con misma descripción
  y fechas distintas),
- lugares incompatibles (atributos de lugar con >1 valor),
- nombres incompatibles (atributos de nombre/nacionalidad/alias con >1 valor).

Conserva todos los candidatos con su procedencia. Genérico: clasifica por el nombre
del campo, sin reglas específicas de ningún caso.
"""

from app.ere.models import slugify
from app.dossier.models import Conflict


def _classify(field_name: str) -> str:
    f = field_name.lower()
    if "date" in f or "fecha" in f or "born" in f or "death" in f:
        return "date"
    if any(k in f for k in ("location", "place", "city", "lugar", "address", "nationality")):
        return "place" if "nationality" not in f else "name"
    if any(k in f for k in ("name", "nombre", "alias")):
        return "name"
    return "generic"


def _distinct(claims) -> list[dict]:
    out: list[dict] = []
    for claim in claims:
        if claim.value not in [c["value"] for c in out]:
            out.append({"value": claim.value, "provider": claim.provider,
                        "confidence": claim.confidence})
    return out


class ConflictEngine:
    def detect(self, people, timeline) -> list[Conflict]:
        conflicts: list[Conflict] = []

        # atributos de persona con >1 valor distinto
        for person in people:
            for field_name, claims in person.attributes.items():
                candidates = _distinct(claims)
                if len(candidates) > 1:
                    conflicts.append(Conflict(
                        type=_classify(field_name), subject=person.id,
                        field=field_name, candidates=candidates,
                    ))

        # eventos con misma descripción pero fechas distintas
        by_desc: dict[str, list] = {}
        for event in timeline:
            if event.description and event.date:
                by_desc.setdefault(slugify(event.description), []).append(event)
        for key, group in by_desc.items():
            dates = []
            for event in group:
                if event.date not in [d["value"] for d in dates]:
                    dates.append({"value": event.date, "provider": event.provider,
                                  "confidence": event.confidence})
            if len(dates) > 1:
                conflicts.append(Conflict(
                    type="date", subject=f"timeline:{key}", field="date", candidates=dates,
                ))

        conflicts.sort(key=lambda c: (c.subject, c.field, c.type))
        return conflicts
