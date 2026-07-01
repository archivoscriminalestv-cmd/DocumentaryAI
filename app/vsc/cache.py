"""AssetCache — reutilización de assets por ``reuse_key``.

Evita regenerar entornos/localizaciones idénticas: si dos peticiones comparten
``reuse_key`` no vacío, se reutiliza el mismo asset (p.ej.
``corner_finestrelles_almassora``). ``reuse_key`` vacío => nunca cachea (único).
"""

from app.vsc.models import GeneratedAsset


class AssetCache:
    def __init__(self) -> None:
        self._by_key: dict[str, GeneratedAsset] = {}

    def get(self, reuse_key: str) -> GeneratedAsset | None:
        if not reuse_key:
            return None
        return self._by_key.get(reuse_key)

    def put(self, asset: GeneratedAsset) -> None:
        if asset.reuse_key:
            self._by_key.setdefault(asset.reuse_key, asset)

    def has(self, reuse_key: str) -> bool:
        return bool(reuse_key) and reuse_key in self._by_key
