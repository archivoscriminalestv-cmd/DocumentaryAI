"""Claim — afirmación sostenida por evidencia.

WP-0025 OBJ-023. Una Claim conserva trazabilidad a la evidencia que la respalda
mediante ``evidence_ids`` (ARCH-0002 AP-004) y a su Research (ADR-0001).
ARCH-0002 AP-003: no hay conocimiento sin evidencia que lo soporte.
"""

from dataclasses import dataclass, field


@dataclass
class Claim:
    id: str
    research_id: str
    statement: str
    evidence_ids: list[str] = field(default_factory=list)
