"""Observabilidad del VPL — progreso + logging estructurado, thread-safe.

Registra inicio, proveedor, prompt hash, cache hit, retry, fallo, finalización y
duración. Contadores protegidos por lock (los workers son concurrentes).
"""

import hashlib
import logging
import threading


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256((prompt or "").encode("utf-8")).hexdigest()[:12]


class Progress:
    def __init__(self, total: int, logger: logging.Logger | None = None) -> None:
        self.total = total
        self.completed = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.failures = 0
        self.retries = 0
        self._lock = threading.Lock()
        self._log = logger or logging.getLogger("vpl")

    def start(self, shot_id: str, provider: str, prompt: str) -> None:
        self._log.info("VPL start shot=%s provider=%s prompt_hash=%s", shot_id, provider, prompt_hash(prompt))

    def cache_hit(self, shot_id: str) -> None:
        with self._lock:
            self.cache_hits += 1
            self.completed += 1
        self._log.info("VPL cache_hit shot=%s", shot_id)

    def retry(self, shot_id: str, attempt: int) -> None:
        with self._lock:
            self.retries += 1
        self._log.warning("VPL retry shot=%s attempt=%d", shot_id, attempt)

    def failure(self, shot_id: str, error: str) -> None:
        with self._lock:
            self.failures += 1
            self.completed += 1
        self._log.error("VPL failure shot=%s error=%s", shot_id, error)

    def complete(self, shot_id: str, duration: float) -> None:
        with self._lock:
            self.cache_misses += 1
            self.completed += 1
        self._log.info("VPL complete shot=%s duration=%.3fs", shot_id, duration)
