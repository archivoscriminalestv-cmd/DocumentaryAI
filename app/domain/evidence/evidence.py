"""Evidence — información que apoya o refuta una afirmación.

ARCH-0002 AP-003: "Evidence precedes interpretation". WP-0025 OBJ-020. Conserva
trazabilidad a su origen mediante ``source_id`` (ARCH-0002 AP-004: la
procedencia es obligatoria, "never optional") y a su Research (ADR-0001).
"""

from dataclasses import dataclass


@dataclass
class Evidence:
    id: str
    research_id: str
    source_id: str
    content: str
