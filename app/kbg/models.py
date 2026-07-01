"""Modelos del Knowledge Bridge (KBG).

Tipados, versionados, serializables, deterministas. Cada ``Decision`` es trazable: lleva
``origin``, ``confidence`` (derivada SOLO del conocimiento disponible), ``knowledge_sources``
y ``reason``. ``GenerationKnowledge`` agrupa las decisiones por sección.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.kbg import KBG_VERSION, SCHEMA_VERSION, UNKNOWN


@dataclass
class Decision:
    key: str
    value: Any = UNKNOWN
    origin: str = UNKNOWN                       # de qué conocimiento procede
    confidence: float = 0.0                     # 0..1, solo del dato disponible
    knowledge_sources: list[str] = field(default_factory=list)
    reason: str = ""

    @property
    def known(self) -> bool:
        return self.value != UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GenerationKnowledge:
    schema_version: str = SCHEMA_VERSION
    kbg_version: str = KBG_VERSION
    genre: str = UNKNOWN
    sections: dict[str, list[Decision]] = field(default_factory=dict)
    summary: dict = field(default_factory=dict)

    def all_decisions(self) -> list[Decision]:
        return [d for decisions in self.sections.values() for d in decisions]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kbg_version": self.kbg_version,
            "genre": self.genre,
            "sections": {name: [d.to_dict() for d in decisions]
                         for name, decisions in self.sections.items()},
            "summary": self.summary,
        }
