"""Almacenamiento físico permanente del ALR.

Estructura (direccionada por contenido):

    library/
      images/    asset_<sha8>.<ext>
      metadata/  asset_<sha8>.json
      asset_registry.json

Reglas duras:
- NUNCA sobreescribe una imagen existente (si el asset_id ya tiene fichero, se respeta).
- NUNCA borra.
El nombre del archivo es el ``asset_id`` (no depende del documental ni del render).
"""

import json
import os

_EXT_BY_FORMAT = {"PNG": ".png", "JPEG": ".jpg", "JPG": ".jpg", "WEBP": ".webp"}


class LibraryStorage:
    def __init__(self, root: str = "library") -> None:
        self.root = root
        self.images_dir = os.path.join(root, "images")
        self.metadata_dir = os.path.join(root, "metadata")
        self.registry_path = os.path.join(root, "asset_registry.json")

    def ensure(self) -> None:
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)

    @staticmethod
    def ext_for(fmt: str) -> str:
        return _EXT_BY_FORMAT.get((fmt or "PNG").upper(), ".png")

    def image_filename(self, asset_id: str, fmt: str) -> str:
        return f"{asset_id}{self.ext_for(fmt)}"

    def image_path(self, asset_id: str, fmt: str) -> str:
        return os.path.join(self.images_dir, self.image_filename(asset_id, fmt))

    def has_image(self, asset_id: str, fmt: str) -> bool:
        return os.path.exists(self.image_path(asset_id, fmt))

    def write_image(self, asset_id: str, fmt: str, data: bytes) -> str:
        """Escribe la imagen SOLO si no existe (idempotente, nunca sobreescribe).

        Devuelve el nombre de archivo relativo dentro de ``images/``.
        """
        self.ensure()
        path = self.image_path(asset_id, fmt)
        filename = self.image_filename(asset_id, fmt)
        if os.path.exists(path):
            return filename  # ya existe: se respeta el binario permanente
        with open(path, "wb") as handle:
            handle.write(data)
        return filename

    def write_metadata(self, asset_id: str, payload: dict) -> str:
        self.ensure()
        path = os.path.join(self.metadata_dir, f"{asset_id}.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        return path

    def load_registry(self) -> dict:
        if not os.path.exists(self.registry_path):
            return {}
        try:
            with open(self.registry_path, encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, json.JSONDecodeError):
            return {}

    def write_registry(self, payload: dict) -> str:
        self.ensure()
        with open(self.registry_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        return self.registry_path
