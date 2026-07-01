"""Registro en memoria + persistencia del ALR (asset_registry.json).

El registro es el índice de TODOS los assets. Carga/guarda de forma reproducible
(``sort_keys``). No elimina nunca: solo añade assets o referencias.
"""

from typing import Iterable

from app.alr import SCHEMA_VERSION
from app.alr.models import Asset
from app.alr.storage import LibraryStorage


class AssetRegistry:
    def __init__(self, storage: LibraryStorage | None = None) -> None:
        self.storage = storage or LibraryStorage()
        self._assets: dict[str, Asset] = {}
        self._by_sha: dict[str, str] = {}   # sha256 -> asset_id (deduplicación exacta)

    # ------------------------------------------------------------------ carga/guardado

    def load(self) -> "AssetRegistry":
        payload = self.storage.load_registry()
        for asset_id, data in (payload.get("assets", {}) or {}).items():
            asset = Asset.from_dict(data)
            self._assets[asset_id] = asset
            if asset.sha256:
                self._by_sha[asset.sha256] = asset_id
        return self

    def to_payload(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "count": len(self._assets),
            "assets": {aid: a.to_dict() for aid, a in self._assets.items()},
        }

    def save(self) -> str:
        return self.storage.write_registry(self.to_payload())

    # ------------------------------------------------------------------ acceso

    def __len__(self) -> int:
        return len(self._assets)

    def __contains__(self, asset_id: str) -> bool:
        return asset_id in self._assets

    def get(self, asset_id: str) -> Asset | None:
        return self._assets.get(asset_id)

    def all(self) -> list[Asset]:
        return list(self._assets.values())

    def by_sha256(self, sha256: str) -> Asset | None:
        aid = self._by_sha.get(sha256)
        return self._assets.get(aid) if aid else None

    def add(self, asset: Asset) -> Asset:
        """Inserta un asset nuevo. Si el id ya existe, devuelve el existente (no pisa)."""
        if asset.asset_id in self._assets:
            return self._assets[asset.asset_id]
        self._assets[asset.asset_id] = asset
        if asset.sha256:
            self._by_sha[asset.sha256] = asset.asset_id
        return asset

    def iter_assets(self) -> Iterable[Asset]:
        return iter(self._assets.values())
