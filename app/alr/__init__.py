"""Asset Library & Registry (ALR) — Sprint ALR-001.

Fuente OFICIAL de verdad de TODOS los recursos audiovisuales generados. Filosofía:
cada asset generado es PERMANENTE — nunca se elimina, nunca se sobreescribe, nunca
cambia de id. El render solo REFERENCIA assets; nunca los reemplaza.

Subsistema completamente ADITIVO e independiente. No modifica CRE/CCE/ERE/VIS/VAI/
VSC/VPL/Composer/Motion/FFmpeg. Se integra DESPUÉS del VPL: registra cada imagen ya
generada, deduplica por contenido y devuelve un ``asset_id`` estable + su ruta
permanente.

    library/
      images/    asset_<sha8>.png        (direccionado por contenido)
      metadata/  asset_<sha8>.json
      asset_registry.json                (índice de todos los assets)
"""

SCHEMA_VERSION = "1.0"

from app.alr.models import Asset, AssetReference
from app.alr.orchestrator import AssetLibrary
from app.alr.registry import AssetRegistry
from app.alr.search import search_assets
from app.alr.storage import LibraryStorage

__all__ = [
    "SCHEMA_VERSION",
    "Asset",
    "AssetReference",
    "AssetLibrary",
    "AssetRegistry",
    "LibraryStorage",
    "search_assets",
]
