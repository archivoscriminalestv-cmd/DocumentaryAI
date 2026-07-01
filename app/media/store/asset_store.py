"""AssetStore — persistencia de assets en filesystem + índice JSON (Fase 1).

Sin dependencias externas: un índice ``index.json`` guarda los metadatos de cada
Asset; los ficheros de media viven junto a él. Estable y suficiente para Fase 1;
sustituible por SQLite/embeddings más adelante sin cambiar la interfaz.
"""

import json
import os

from app.media.store.models import Asset


class AssetStore:
    def __init__(self, base_dir: str = os.path.join("output", "media_assets")) -> None:
        self._dir = base_dir
        os.makedirs(self._dir, exist_ok=True)
        self._index_path = os.path.join(self._dir, "index.json")
        self._items: dict[str, Asset] = self._load()

    @property
    def base_dir(self) -> str:
        return self._dir

    def add(self, asset: Asset) -> Asset:
        self._items[asset.asset_id] = asset
        self._save()
        return asset

    def get(self, asset_id: str) -> Asset | None:
        return self._items.get(asset_id)

    def all(self) -> list[Asset]:
        return list(self._items.values())

    def increment_reuse(self, asset_id: str) -> None:
        asset = self._items.get(asset_id)
        if asset is not None:
            asset.reuse_count += 1
            self._save()

    def register_reuse(self, asset_id: str, scene_id: str = "") -> Asset | None:
        """Marca un asset como reutilizado: ++reuse_count y registra la nueva escena."""
        asset = self._items.get(asset_id)
        if asset is None:
            return None
        asset.reuse_count += 1
        if scene_id and scene_id != asset.scene_id and scene_id not in asset.reused_scene_ids:
            asset.reused_scene_ids.append(scene_id)
        self._save()
        return asset

    def find_by_prompt(self, prompt: str) -> list[Asset]:
        """Búsqueda exacta por prompt (normalizado). Útil para el reuse engine."""
        target = " ".join((prompt or "").lower().split())
        return [a for a in self._items.values() if " ".join(a.prompt.lower().split()) == target]

    def _load(self) -> dict[str, Asset]:
        if not os.path.exists(self._index_path):
            return {}
        try:
            with open(self._index_path, encoding="utf-8") as handle:
                raw = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return {}
        return {a["asset_id"]: Asset.from_dict(a) for a in raw if "asset_id" in a}

    def _save(self) -> None:
        data = [asset.to_dict() for asset in self._items.values()]
        with open(self._index_path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
