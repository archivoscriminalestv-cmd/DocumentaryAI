"""Evidence Query Builder (ERE-002) — genera múltiples consultas enriquecidas.

Nunca una única búsqueda: a partir de ``ProjectKnowledge`` cada *estrategia* (plug-in)
produce consultas; el Builder las fusiona, deduplica y ordena por peso. No concatena
texto sin criterio: cada estrategia combina señales con sentido (persona+lugar,
persona+fecha, alias+persona, palabras clave+lugar, combinaciones…).

Determinista y sin red.
"""

import unicodedata
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field

from app.ere.project_knowledge import ProjectKnowledge


@dataclass
class EvidenceQuery:
    text: str
    strategy: str
    target: str = "*"          # proveedor(es) objetivo: "*" o "news,wikipedia"
    weight: float = 0.5        # prioridad (1.0 = más específica/relevante)
    terms: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _norm_text(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text or "")
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii").lower()
    return " ".join(ascii_only.split())


def _year(date: str) -> str:
    digits = "".join(ch for ch in (date or "") if ch.isdigit())
    return digits[:4] if len(digits) >= 4 else ""


def _query(terms: list[str], strategy: str, target: str, weight: float) -> EvidenceQuery | None:
    clean = [t.strip() for t in terms if t and t.strip()]
    if not clean:
        return None
    return EvidenceQuery(text=" ".join(clean), strategy=strategy, target=target,
                         weight=weight, terms=clean)


class QueryStrategy(ABC):
    name = "base"

    @abstractmethod
    def build(self, knowledge: ProjectKnowledge) -> list[EvidenceQuery]:
        ...


def _persons(k: ProjectKnowledge) -> list[str]:
    persons: list[str] = []
    for name in [k.canonical_name, *k.known_people]:
        if name and name not in persons:
            persons.append(name)
    return persons


class PersonStrategy(QueryStrategy):
    name = "person"

    def build(self, k):
        out = []
        for person in _persons(k):
            out.append(_query([person], self.name, "*", 0.55))
            for loc in k.locations:
                out.append(_query([person, loc], self.name, "*", 0.9))
        return [q for q in out if q]


class AliasStrategy(QueryStrategy):
    name = "alias"

    def build(self, k):
        out = []
        subject = k.subject_name()
        aliases = list(k.aliases)
        if k.title and k.title != subject:
            aliases.append(k.title)
        for alias in dict.fromkeys(aliases):
            out.append(_query([alias], self.name, "*", 0.3))
            if subject:
                out.append(_query([alias, subject], self.name, "*", 0.8))
            for loc in k.locations:
                out.append(_query([alias, loc], self.name, "*", 0.6))
        return [q for q in out if q]


class LocationStrategy(QueryStrategy):
    name = "location"

    def build(self, k):
        out = []
        for loc in k.locations:
            for person in _persons(k):
                out.append(_query([person, loc], self.name, "news,wikipedia", 0.85))
        return [q for q in out if q]


class DateStrategy(QueryStrategy):
    name = "date"

    def build(self, k):
        out = []
        subject = k.subject_name()
        for date in k.dates:
            year = _year(date) or date
            out.append(_query([subject, year], self.name, "news", 0.8))
            for loc in k.locations:
                out.append(_query([subject, loc, year], self.name, "news", 0.95))
        return [q for q in out if q]


class KeywordStrategy(QueryStrategy):
    name = "keyword"

    def build(self, k):
        out = []
        subject = k.subject_name()
        for kw in k.keywords:
            if subject:
                out.append(_query([subject, kw], self.name, "news", 0.75))
            for loc in k.locations:
                out.append(_query([kw, loc], self.name, "news", 0.7))
        return [q for q in out if q]


class CombinedStrategy(QueryStrategy):
    name = "combined"

    def build(self, k):
        out = []
        subject = k.subject_name()
        loc = k.locations[0] if k.locations else ""
        year = _year(k.dates[0]) if k.dates else ""
        out.append(_query([subject, loc, year], self.name, "*", 0.99))
        if k.keywords:
            out.append(_query([subject, k.keywords[0], loc], self.name, "*", 0.9))
        if k.title and k.title != subject:
            out.append(_query([k.title, subject, loc], self.name, "*", 0.85))
        return [q for q in out if q]


def default_strategies() -> list[QueryStrategy]:
    return [
        PersonStrategy(), AliasStrategy(), LocationStrategy(),
        DateStrategy(), KeywordStrategy(), CombinedStrategy(),
    ]


class QueryBuilder:
    def __init__(self, strategies: list[QueryStrategy] | None = None) -> None:
        self._strategies = strategies or default_strategies()

    def build(self, knowledge: ProjectKnowledge) -> list[EvidenceQuery]:
        best: dict[str, EvidenceQuery] = {}
        for strategy in self._strategies:
            for query in strategy.build(knowledge):
                key = _norm_text(query.text)
                if not key:
                    continue
                existing = best.get(key)
                # dedupe: se conserva la consulta de mayor peso (estrategia más fuerte)
                if existing is None or query.weight > existing.weight:
                    best[key] = query
        # orden determinista: mayor peso primero, luego alfabético
        return sorted(best.values(), key=lambda q: (-q.weight, _norm_text(q.text)))
