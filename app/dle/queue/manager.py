"""LearningQueueManager — orquesta la cola de aprendizaje masivo (DLE-002).

Procesa la cola automáticamente, un documental tras otro, sin intervención. Persiste el
progreso tras cada transición (resume tras un cierre). No re-aprende lo ya aprendido.
Responsabilidades: añadir / eliminar / pausar / reanudar / cancelar / reintentar /
estado. No modifica el pipeline de generación.
"""

import logging
import os

from app.dle.monitor.events import FINISHED, PROGRESS, STARTED, ProgressEvent, with_context
from app.dle.orchestrator import DocumentaryLearningEngine
from app.dle.queue.index import KnowledgeIndex
from app.dle.queue.job import LearningJob
from app.dle.queue.models import QueueStatus
from app.dle.queue.reports import build_statistics, write_reports
from app.dle.queue.store import QueueStore


def _dir_size(path: str) -> int:
    total = 0
    if not os.path.exists(path):
        return 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except OSError:
                pass
    return total


class LearningQueueManager:
    def __init__(self, *, engine: DocumentaryLearningEngine | None = None,
                 store: QueueStore | None = None, index: KnowledgeIndex | None = None,
                 knowledge_root: str = "knowledge", logger=None, intelligence=None) -> None:
        self.knowledge_root = knowledge_root
        self.engine = engine or DocumentaryLearningEngine()
        self.store = store or QueueStore(os.path.join(knowledge_root, "learning_queue.json"))
        self.index = index or KnowledgeIndex(os.path.join(knowledge_root, "learning_index.json"))
        self._log = logger or logging.getLogger("dle.queue")
        self.intelligence = intelligence   # YIE (opcional): Queue -> YIE -> DLE
        self._history: list[dict] = []

    # ------------------------------------------------------------------ gestión
    def add_urls(self, urls: list[str]) -> int:
        added = 0
        for url in urls:
            url = (url or "").strip()
            if not url or url.startswith("#"):
                continue
            before = self.store.get(url)
            self.store.add(url)
            if before is None:
                added += 1
        self.store.save()
        return added

    def add_from_file(self, path: str) -> int:
        with open(path, encoding="utf-8") as h:
            return self.add_urls([line for line in h])

    def remove(self, url: str) -> bool:
        ok = self.store.remove(url)
        self.store.save()
        return ok

    def cancel(self, url: str) -> bool:
        item = self.store.get(url)
        if item and item.status not in QueueStatus.TERMINAL:
            return self.remove(url)
        return False

    def pause(self) -> None:
        self.store.set_paused(True)
        self.store.save()

    def resume(self) -> None:
        self.store.set_paused(False)
        self.store.save()

    def retry(self) -> int:
        n = 0
        for item in self.store.by_status(QueueStatus.FAILED):
            item.status = QueueStatus.PENDING
            item.error = ""
            n += 1
        self.store.save()
        return n

    def clear_finished(self) -> int:
        n = self.store.clear_finished()
        self.store.save()
        return n

    def status(self) -> dict:
        return build_statistics(self.store, self.knowledge_root)

    # ------------------------------------------------------------------ proceso
    def process_all(self, *, limit: int | None = None, max_attempts: int = 3,
                    on_event=None) -> dict:
        """``on_event(ProgressEvent)`` (opcional, aditivo) emite eventos públicos de
        progreso para el monitor. No altera el procesamiento."""
        recovered = self.store.recover_inflight()   # reanuda trabajos interrumpidos
        if recovered:
            self.store.save()
        job = LearningJob(self.engine, self.index, save_cb=self.store.save,
                          intelligence=self.intelligence)

        pending = [i for i in self.store.ordered() if i.status == QueueStatus.PENDING]
        total = len(pending) if limit is None else min(limit, len(pending))
        if on_event is not None:
            on_event(ProgressEvent(kind=STARTED, stage="queue", total=total,
                                   metrics=self._metrics_snapshot()))

        processed = 0
        if self.store.is_paused():
            self._log.info("DLE queue: en pausa; no se procesa")
        else:
            for item in self.store.ordered():
                if self.store.is_paused():
                    break
                if limit is not None and processed >= limit:
                    break
                if item.status != QueueStatus.PENDING:
                    continue
                if item.attempts >= max_attempts:
                    item.status = QueueStatus.FAILED
                    item.error = item.error or f"máx. intentos ({max_attempts}) alcanzado"
                    self.store.save()
                    continue
                self._log.info("DLE queue: procesando %s", item.url)
                # Contexto de cola (posición/total/doc) que el orquestador no conoce.
                ctx = with_context(on_event, position=processed + 1, total=total,
                                   doc_ref=item.url)
                if ctx is not None:
                    ctx(ProgressEvent(kind=STARTED, stage="item"))
                job.run(item, on_event=ctx)
                if on_event is not None:
                    on_event(ProgressEvent(kind=PROGRESS, stage="queue",
                                           metrics=self._metrics_snapshot()))
                self._history.append({"url": item.url, "status": item.status,
                                      "documentary_id": item.documentary_id,
                                      "attempts": item.attempts})
                processed += 1

        self.index.save()
        paths = write_reports(self.store, self._history, self.knowledge_root)
        if on_event is not None:
            on_event(ProgressEvent(kind=FINISHED, stage="queue",
                                   metrics=self._metrics_snapshot()))
        return {"processed": processed, "recovered": recovered,
                "status": self.status(), "reports": paths}

    def _metrics_snapshot(self) -> dict:
        stats = self.status()
        return {
            "documentaries_learned": stats["documentaries_learned"],
            "hours_learned": stats["hours_learned"],
            "kb_size_bytes": _dir_size(os.path.join(self.knowledge_root, "documentaries")),
        }
