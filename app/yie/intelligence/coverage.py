"""Auditoría de cobertura de proveedores (YIE-002).

Construye ``provider_coverage.json``: para cada campo relevante, de qué proveedor
provino (yt-dlp / vidiq / derived / …) o ``UNKNOWN`` si quedó sin dato. Hace que la
calidad de la base de conocimiento sea completamente auditable (ADR-0012).
"""

from app.yie import UNKNOWN
from app.yie.intelligence.models import ProviderCoverage


def _known(value) -> bool:
    return value not in (None, "", UNKNOWN, [], {})


def build_coverage(fields: dict, origins: dict,
                   providers_available: list[str],
                   providers_unavailable: list[str]) -> ProviderCoverage:
    """``fields``: {nombre: valor}; ``origins``: {nombre: proveedor que lo aportaría}."""
    by_field: dict[str, str] = {}
    known = 0
    for name in sorted(fields):
        if _known(fields[name]):
            by_field[name] = origins.get(name, "yt-dlp")
            known += 1
        else:
            by_field[name] = "UNKNOWN"
    total = len(fields)
    return ProviderCoverage(
        providers_available=sorted(providers_available),
        providers_unavailable=sorted(providers_unavailable),
        by_field=by_field,
        known_fields=known,
        unknown_fields=total - known,
        coverage_ratio=round(known / total, 4) if total else 0.0,
    )
