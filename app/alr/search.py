"""Buscador interno del ALR.

Consulta el registro por campos intrínsecos (provider/model/prompt/character/identity/
tags/fecha) y por contexto de uso (project/scene/shot, incluyendo las ``references``).
Todos los filtros se combinan con AND. ``prompt`` y ``tag`` son subcadena/contiene.
"""

from app.alr.models import Asset
from app.alr.registry import AssetRegistry


def _matches(asset: Asset, key: str, value: str) -> bool:
    v = str(value).lower()
    if key == "asset_id":
        return asset.asset_id.lower() == v
    if key == "provider":
        return asset.provider.lower() == v
    if key == "model":
        return v in asset.model.lower()
    if key == "prompt":
        return v in asset.prompt.lower()
    if key in ("character", "character_name"):
        return v in asset.character_name.lower()
    if key in ("identity", "character_identity"):
        return asset.character_identity.lower() == v
    if key == "tag":
        return any(v == t.lower() for t in asset.tags)
    if key == "date":
        return asset.created_at.startswith(value)
    # Contexto de uso: comprueba el origen y TODAS las referencias.
    if key in ("project", "scene", "shot"):
        if str(getattr(asset, key, "")).lower() == v:
            return True
        return any(str(getattr(ref, key, "")).lower() == v for ref in asset.references)
    # Campo arbitrario: igualdad sobre atributo intrínseco si existe.
    return str(getattr(asset, key, "")).lower() == v


def search_assets(registry: AssetRegistry, **filters) -> list[Asset]:
    """Devuelve los assets que cumplen TODOS los filtros (None/"" se ignoran)."""
    active = {k: val for k, val in filters.items() if val not in (None, "")}
    results = [
        a for a in registry.all()
        if all(_matches(a, k, val) for k, val in active.items())
    ]
    results.sort(key=lambda a: a.asset_id)
    return results
