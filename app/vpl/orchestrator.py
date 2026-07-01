"""VisualGenerationOrchestrator — coordina la generación visual del VPL.

Recibe VisualGenerationRequests, busca en caché, despacha a los workers (paralelo)
con política de reintentos, normaliza la salida del proveedor a GeneratedAsset,
escribe imágenes + metadata + manifest y reporta progreso. NO conoce internals de
ningún proveedor (solo la interfaz ``VisualProvider``).
"""

import hashlib
import json
import logging
import os
import threading
import time
from datetime import datetime, timezone

from app.vpl.cache import AssetCache
from app.vpl.config import VPLConfig, build_provider
from app.vpl.models import GeneratedAsset, GenerationFailure, GenerationManifest
from app.vpl.progress import Progress
from app.vpl.queue import WorkerPool
from app.vpl.retry import run_with_retry


class VisualGenerationOrchestrator:
    def __init__(self, config=None, provider=None, cache=None, logger=None, sleep=time.sleep) -> None:
        self._config = config or VPLConfig.from_env()
        self._provider = provider or build_provider(self._config)
        self._cache = cache or AssetCache(self._config.cache_dir)
        self._log = logger or logging.getLogger("vpl")
        self._sleep = sleep
        # Locks por clave de caché: serializan la generación de claves idénticas
        # bajo concurrencia (reutilización determinista, sin trabajo duplicado);
        # claves distintas siguen en paralelo.
        self._locks: dict[str, threading.Lock] = {}
        self._locks_guard = threading.Lock()

    def _key_lock(self, key: str) -> threading.Lock:
        with self._locks_guard:
            lock = self._locks.get(key)
            if lock is None:
                lock = threading.Lock()
                self._locks[key] = lock
            return lock

    def generate(self, requests: list, *, documentary_id: str, output_dir: str) -> GenerationManifest:
        images_dir = os.path.join(output_dir, "images")
        meta_dir = os.path.join(output_dir, "metadata")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(meta_dir, exist_ok=True)

        provider = self._provider
        progress = Progress(len(requests), self._log)
        started = time.perf_counter()

        results = WorkerPool(self._config.workers).map(
            lambda item: self._handle(item, provider, progress, images_dir, meta_dir),
            list(enumerate(requests)),
        )

        assets = [r[1].to_dict() for r in results if r and r[0] == "asset"]
        failed = [r[1].to_dict() for r in results if r and r[0] == "fail"]

        manifest = GenerationManifest(
            documentary_id=documentary_id,
            provider=provider.name,
            model=getattr(provider, "model", ""),
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_seconds=round(time.perf_counter() - started, 3),
            total=len(requests),
            cache_hits=progress.cache_hits,
            cache_misses=progress.cache_misses,
            failures=progress.failures,
            retries=progress.retries,
            assets=assets,
            failed=failed,
        )
        with open(os.path.join(output_dir, "manifest.json"), "w", encoding="utf-8") as handle:
            json.dump(manifest.to_dict(), handle, ensure_ascii=False, indent=2)
        self._log.info("VPL manifest documentary=%s assets=%d failures=%d cache_hits=%d",
                       documentary_id, len(assets), len(failed), progress.cache_hits)
        return manifest

    def _handle(self, item, provider, progress, images_dir, meta_dir):
        index, request = item
        filename = f"S{index + 1:02d}.png"
        shot_id = str(getattr(request, "shot_id", f"shot-{index}"))
        scene_id = str(getattr(request, "scene_id", ""))
        progress.start(shot_id, provider.name, getattr(request, "prompt", ""))
        try:
            key = self._cache.key(request, provider.name, getattr(provider, "model", ""))
            cached = self._cache.get(key)
            if cached is None:
                # Doble verificación bajo el lock de la clave (otro worker pudo
                # generar la misma clave mientras esperábamos).
                with self._key_lock(key):
                    cached = self._cache.get(key)
                    if cached is None:
                        return self._generate(request, provider, progress, images_dir, meta_dir, filename, key, shot_id)

            image_bytes, meta = cached
            fields = GeneratedAsset.__dataclass_fields__
            asset = GeneratedAsset(**{k: v for k, v in meta.items() if k in fields})
            asset.cached = True
            asset.status = "cached"
            asset.created_at = datetime.now(timezone.utc).isoformat()
            asset.filename = filename
            self._write(images_dir, meta_dir, filename, image_bytes, asset)
            progress.cache_hit(shot_id)
            return ("asset", asset)
        except Exception as exc:
            progress.failure(shot_id, str(exc))
            return ("fail", GenerationFailure(
                shot_id=shot_id, scene_id=scene_id, error=str(exc),
                created_at=datetime.now(timezone.utc).isoformat(),
            ))

    def _generate(self, request, provider, progress, images_dir, meta_dir, filename, key, shot_id):
        t0 = time.perf_counter()
        asset, _retries = run_with_retry(
            lambda: provider.generate(request),
            max_retries=self._config.max_retries,
            base_delay=self._config.base_delay,
            sleep=self._sleep,
            on_retry=lambda attempt, exc: progress.retry(shot_id, attempt),
        )
        image_bytes = asset.image_bytes or b""
        asset.filename = filename
        asset.hash = hashlib.sha256(image_bytes).hexdigest()
        asset.created_at = datetime.now(timezone.utc).isoformat()
        asset.status = "generated"
        if not asset.generation_time:
            asset.generation_time = round(time.perf_counter() - t0, 3)
        self._cache.put(key, image_bytes, asset.to_dict())
        self._write(images_dir, meta_dir, filename, image_bytes, asset)
        progress.complete(shot_id, asset.generation_time)
        return ("asset", asset)

    @staticmethod
    def _write(images_dir, meta_dir, filename, image_bytes, asset: GeneratedAsset) -> None:
        with open(os.path.join(images_dir, filename), "wb") as handle:
            handle.write(image_bytes)
        meta_name = os.path.splitext(filename)[0] + ".json"
        with open(os.path.join(meta_dir, meta_name), "w", encoding="utf-8") as handle:
            json.dump(asset.to_dict(), handle, ensure_ascii=False, indent=2)
