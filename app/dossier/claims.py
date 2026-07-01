"""Modelo de afirmación trazable del dossier.

Toda afirmación del DocumentaryDossier es un ``DossierClaim`` con su procedencia:
``confidence``, ``provider``, ``source_url``, ``license``. Nunca hay un dato sin
origen. Aquí también se convierten los ``Claim`` del EvidenceGraph (ERE) en
``DossierClaim`` resolviendo la licencia desde las fuentes de la entidad.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class DossierClaim:
    field: str
    value: Any
    confidence: float = 0.0
    provider: str = ""
    source_url: str = ""
    license: str = ""


def license_lookup(sources) -> dict[str, str]:
    """{provider: license} a partir de una lista de SourceRef (del EvidenceGraph)."""
    out: dict[str, str] = {}
    for src in sources:
        if getattr(src, "provider", "") and getattr(src, "license", ""):
            out.setdefault(src.provider, src.license)
    return out


def from_ere_claim(claim, licenses: dict[str, str]) -> DossierClaim:
    return DossierClaim(
        field=claim.field,
        value=claim.value,
        confidence=claim.confidence,
        provider=claim.provider,
        source_url=getattr(claim, "source", "") or "",
        license=licenses.get(claim.provider, ""),
    )
