"""Deduplicación del ALR.

- EXACTA: mismo SHA256 -> es el mismo asset. No se copia; solo se añade una referencia.
- PERCEPTUAL: pHash cercano (Hamming <= umbral) -> se marca ``possible_duplicate``,
  pero NUNCA se elimina ni se fusiona (decisión humana posterior).
"""

from app.alr.fingerprint import hamming
from app.alr.models import Asset
from app.alr.registry import AssetRegistry

# Umbral por defecto de similitud perceptual (en bits de un pHash de 64 bits).
DEFAULT_PHASH_THRESHOLD = 6


def find_exact(registry: AssetRegistry, sha256: str) -> Asset | None:
    return registry.by_sha256(sha256)


def find_perceptual(registry: AssetRegistry, phash: str,
                    *, threshold: int = DEFAULT_PHASH_THRESHOLD,
                    exclude_sha: str = "") -> list[str]:
    """Ids de assets visualmente cercanos (sin ser idénticos por contenido)."""
    if not phash:
        return []
    near: list[tuple[int, str]] = []
    for asset in registry.iter_assets():
        if not asset.phash or asset.sha256 == exclude_sha:
            continue
        distance = hamming(phash, asset.phash)
        if distance <= threshold:
            near.append((distance, asset.asset_id))
    near.sort()
    return [aid for _d, aid in near]
