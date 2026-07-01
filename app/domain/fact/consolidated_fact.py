"""ConsolidatedFact — unidad de verdad consolidada desde evidencia (Sprint C-05).

Objeto de dominio puro y DISTINTO del ``Fact`` existente (pipeline:
id/evidence_id/text). Aquí una ``statement`` atómica queda respaldada por una o
más evidencias y conserva la procedencia completa (``evidence_ids`` ->
``source_ids``). Es aditivo: no toca ``fact.py`` ni el pipeline existente.

``confidence`` es ``float`` -> serializable a JSON directamente.
"""

from dataclasses import dataclass, field


@dataclass
class ConsolidatedFact:
    id: str
    statement: str
    confidence: float
    evidence_ids: list[str] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
