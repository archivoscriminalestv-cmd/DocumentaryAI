"""ImageCache — caché de imágenes por prompt (Sprint C-10).

Clave: sha256(image_prompt). Evita regenerar prompts idénticos. Si la imagen ya
existe en ``{base_dir}/images/{hash}.png`` se reutiliza (cache_hit=True); si no,
se genera con el ``ImageRenderer`` inyectado y se guarda con sus metadatos.
"""

import hashlib
import json
import os
import time


class ImageCache:
    def __init__(self, renderer=None, base_dir: str = "cache") -> None:
        self._renderer = renderer
        self._images_dir = os.path.join(base_dir, "images")
        os.makedirs(self._images_dir, exist_ok=True)

    @staticmethod
    def key(image_prompt: str) -> str:
        return hashlib.sha256(image_prompt.encode("utf-8")).hexdigest()

    def get_or_render(
        self, *, image_prompt: str, scene_id: str
    ) -> tuple[str, bool, bool]:
        """Devuelve (image_path, cache_hit, rendered)."""
        digest = self.key(image_prompt)
        path = os.path.join(self._images_dir, f"{digest}.png")

        if os.path.exists(path) and os.path.getsize(path) > 0:
            return path, True, True

        rendered = False
        if self._renderer is not None:
            rendered = self._renderer.render(image_prompt, path)
        if rendered:
            self._write_metadata(digest, image_prompt, scene_id)
        return path, False, rendered

    def _write_metadata(self, digest: str, image_prompt: str, scene_id: str) -> None:
        meta = {
            "hash": digest,
            "prompt_length": len(image_prompt),
            "scene_id": scene_id,
            "timestamp": time.time(),
        }
        meta_path = os.path.join(self._images_dir, f"{digest}.json")
        try:
            with open(meta_path, "w", encoding="utf-8") as handle:
                json.dump(meta, handle, ensure_ascii=False)
        except OSError:
            pass
