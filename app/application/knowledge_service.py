"""KnowledgeService — construye relaciones entre hechos (Sprint C-06).

Constructor de grafo de conocimiento DETERMINISTA, sin IA y sin inventar nada:

- Trabaja SOLO sobre el texto de los ``ConsolidatedFact`` de entrada.
- Forma relaciones por PARES (unidad mínima válida): nunca fusiona todos los
  hechos en un único nodo. Cada relación conecta exactamente 2 hechos por un
  conector presente en el texto (entidad/fecha/lugar compartido o marcador
  explícito), y expresa UNA sola relación.
- Tipo estricto: causal | temporal | hierarchical | geographical | associative.
- ``statement`` = conector + las dos afirmaciones VERBATIM (cero invención).
- Procedencia: ``fact_ids`` (ambos) y ``source_ids`` (unión deduplicada).
- ``confidence`` = mínimo de los hechos de la relación.
- Sin relaciones posibles -> ``[]``.

LÍMITE CONOCIDO: la equivalencia semántica/ sinónima profunda requiere un LLM y
queda fuera de esta capa; aquí se relaciona por señales léxicas explícitas.
"""

import re

from app.domain.knowledge.knowledge_relation import KnowledgeRelation, RelationshipType

_WORD = re.compile(r"[a-z0-9]+")
_YEAR = re.compile(r"\b(?:1\d{3}|20\d{2})\b")
_MONTHS = {
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december",
}
_GEO_PREP = {"in", "at", "near", "from", "across", "around", "within"}
_CAUSAL_MARKERS = (
    "because", "caused", "due to", "led to", "leading to", "resulted in",
    "results in", "result of", "triggered", "as a result", "cause of",
)
_HIER_MARKERS = (
    "part of", "type of", "types of", "kind of", "category", "categories",
    "consists of", "comprises", "includes", "member of", "subset of",
    "belongs to", "classified as",
)
_STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "at", "to", "and", "or", "is", "was",
    "were", "are", "be", "been", "it", "its", "that", "this", "these", "those",
    "for", "with", "as", "by", "from", "into", "near", "over", "after", "before",
    "had", "has", "have", "very", "had", "their", "they",
}


class _Analysis:
    __slots__ = ("entities", "temporal", "places", "has_causal", "has_hier")

    def __init__(self, entities, temporal, places, has_causal, has_hier):
        self.entities = entities
        self.temporal = temporal
        self.places = places
        self.has_causal = has_causal
        self.has_hier = has_hier


def _places(statement: str) -> set[str]:
    words = statement.split()
    found: set[str] = set()
    for i in range(len(words) - 1):
        if words[i].lower().strip(".,;:'\"") in _GEO_PREP:
            nxt = words[i + 1].strip(".,;:'\"()")
            if nxt[:1].isupper():
                found.add(nxt.lower())
    return found


def _analyze(statement: str) -> _Analysis:
    lower = statement.lower()
    raw = _WORD.findall(lower)
    temporal = set(_YEAR.findall(statement)) | {m for m in _MONTHS if m in raw}
    places = _places(statement)
    entities = {
        t for t in raw
        if len(t) >= 3 and t not in _STOPWORDS and t not in temporal and t not in places
    }
    has_causal = any(m in lower for m in _CAUSAL_MARKERS)
    has_hier = any(m in lower for m in _HIER_MARKERS)
    return _Analysis(entities, temporal, places, has_causal, has_hier)


def _classify(a: _Analysis, b: _Analysis) -> tuple[str, str] | None:
    """Devuelve (relationship_type, connector) o None si no hay relación."""
    shared_entities = sorted(a.entities & b.entities)
    shared_temporal = sorted(a.temporal & b.temporal)
    shared_places = sorted(a.places & b.places)

    if shared_entities and (a.has_causal or b.has_causal):
        return RelationshipType.CAUSAL, shared_entities[0]
    if shared_temporal:
        return RelationshipType.TEMPORAL, shared_temporal[0]
    if shared_places:
        return RelationshipType.GEOGRAPHICAL, shared_places[0]
    if shared_entities and (a.has_hier or b.has_hier):
        return RelationshipType.HIERARCHICAL, shared_entities[0]
    if shared_entities:
        return RelationshipType.ASSOCIATIVE, shared_entities[0]
    return None


def _union(a: list[str], b: list[str]) -> list[str]:
    out: list[str] = []
    for value in list(a) + list(b):
        if value and value not in out:
            out.append(value)
    return out


class KnowledgeService:
    def build(self, facts: list) -> list[KnowledgeRelation]:
        valid = [f for f in (facts or []) if getattr(f, "statement", None) and getattr(f, "id", None)]
        if len(valid) < 2:
            return []

        analyses = [_analyze(str(f.statement)) for f in valid]

        relations: list[KnowledgeRelation] = []
        seq = 0
        for i in range(len(valid)):
            for j in range(i + 1, len(valid)):
                classified = _classify(analyses[i], analyses[j])
                if classified is None:
                    continue
                rel_type, connector = classified
                fi, fj = valid[i], valid[j]
                seq += 1
                relations.append(
                    KnowledgeRelation(
                        id=f"know-{seq:02d}",
                        statement=f"[{connector}] {fi.statement} | {fj.statement}",
                        fact_ids=[str(fi.id), str(fj.id)],
                        source_ids=_union(
                            list(getattr(fi, "source_ids", []) or []),
                            list(getattr(fj, "source_ids", []) or []),
                        ),
                        relationship_type=rel_type,
                        confidence=min(
                            float(getattr(fi, "confidence", 0.0) or 0.0),
                            float(getattr(fj, "confidence", 0.0) or 0.0),
                        ),
                    )
                )
        return relations
