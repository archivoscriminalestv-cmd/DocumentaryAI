"""AssetCache del VPL — caché de assets en disco, persistente entre ejecuciones.

Clave de caché (dos vías, ambas incluyen provider+model para no invalidar assets
no relacionados al cambiar de proveedor):

- ``reuse_key`` no vacío  -> hash(reuse_key|provider|model): localización/asset
  reutilizable nombrado (p.ej. ``corner_finestrelles_almassora``) que se reutiliza
  ENTRE escenas/planos que lo referencian.
- ``reuse_key`` vacío     -> hash(provider|model|seed|prompt_hash): direccionado por
  contenido; idéntica petición -> mismo asset (reutilización entre ejecuciones),
  peticiones distintas -> assets distintos (sin colapso).
"""

import hashlib
import json
import os


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class AssetCache:
    def __init__(self, base_dir: str) -> None:
        self._dir = base_dir
        os.makedirs(self._dir, exist_ok=True)

    def key(self, request, provider: str, model: str) -> str:
        reuse_key = str(getattr(request, "reuse_key", "") or "")
        if reuse_key:
            return _sha(f"loc::{reuse_key}|{provider}|{model}")
        prompt_hash = _sha(f"{getattr(request, 'prompt', '')}||{getattr(request, 'negative_prompt', '')}")
        seed = getattr(request, "seed", 0)
        return _sha(f"content::{provider}|{model}|{seed}|{prompt_hash}")

    def get(self, key: str) -> tuple[bytes, dict] | None:
        png, meta = self._paths(key)
        if os.path.exists(png) and os.path.exists(meta):
            with open(png, "rb") as f_png, open(meta, encoding="utf-8") as f_meta:
                return f_png.read(), json.load(f_meta)
        return None

    def put(self, key: str, image_bytes: bytes, meta: dict) -> None:
        png, meta_path = self._paths(key)
        with open(png, "wb") as f_png:
            f_png.write(image_bytes)
        with open(meta_path, "w", encoding="utf-8") as f_meta:
            json.dump(meta, f_meta, ensure_ascii=False, indent=2)

    def _paths(self, key: str) -> tuple[str, str]:
        return os.path.join(self._dir, f"{key}.png"), os.path.join(self._dir, f"{key}.json")
