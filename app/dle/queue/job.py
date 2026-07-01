"""LearningJob — aprende UN documental (un elemento de la cola).

El Queue Manager solo ejecuta Jobs. El Job: resuelve la fuente, comprueba el índice
(skip antes de descargar), invoca el DLE actualizando el estado en cada etapa (y
persistiendo el progreso), y registra el resultado en el índice. Nunca lanza: traduce
los fallos a estado FAILED.
"""

from app.dle import SCHEMA_VERSION
from app.dle.monitor.events import FAILED, FINISHED, ProgressEvent
from app.dle.queue.downloader import resolve_source
from app.dle.queue.index import KnowledgeIndex
from app.dle.queue.models import STAGE_TO_STATUS, QueueItem, QueueStatus


class LearningJob:
    def __init__(self, engine, index: KnowledgeIndex, save_cb=lambda: None,
                 intelligence=None) -> None:
        self._engine = engine
        self._index = index
        self._save = save_cb
        self._intelligence = intelligence   # YIE (opcional): Queue -> YIE -> DLE

    def run(self, item: QueueItem, on_event=None) -> QueueItem:
        def event(kind, stage, **kw):
            if on_event is not None:
                on_event(ProgressEvent(kind=kind, stage=stage, **kw))

        resolved = resolve_source(item.url)
        if resolved is None:
            item.status = QueueStatus.FAILED
            item.attempts += 1
            item.error = "fuente no reconocida (ni YouTube ni fichero local existente)"
            event(FAILED, "item", error=item.error)
            self._save()
            return item

        item.kind = resolved.kind
        item.video_id = resolved.video_id
        item.documentary_id = resolved.documentary_id

        # YouTube Intelligence (YIE) ANTES del DLE, si está disponible y la fuente es
        # YouTube. Best-effort: nunca rompe la cola ni el DLE.
        if self._intelligence is not None and resolved.kind == "youtube":
            try:
                self._intelligence.inspect(item.url, documentary_id=resolved.documentary_id)
            except Exception:  # noqa: BLE001 — la inteligencia es complementaria
                pass

        # Skip ANTES de descargar: ya aprendido con el esquema actual.
        if (self._index.should_skip(documentary_id=resolved.documentary_id,
                                    video_id=resolved.video_id, url=item.url)
                or self._engine.store.exists(resolved.documentary_id)):
            item.status = QueueStatus.SKIPPED
            item.schema_version = SCHEMA_VERSION
            self._index.record(documentary_id=resolved.documentary_id,
                               video_id=resolved.video_id, canonical_url=item.url,
                               schema_version=SCHEMA_VERSION)
            event(FINISHED, "item", doc_id=item.documentary_id, metrics={"skipped": True})
            self._save()
            return item

        def _on_stage(stage: str) -> None:
            item.status = STAGE_TO_STATUS.get(stage, item.status)
            self._save()                       # progreso persistente (resume-safe)

        try:
            result = self._engine.learn(**resolved.learn_kwargs, on_stage=_on_stage,
                                        on_event=on_event)
        except Exception as exc:  # noqa: BLE001 — un job nunca rompe la cola
            item.status = QueueStatus.FAILED
            item.attempts += 1
            item.error = f"{type(exc).__name__}: {exc}"
            event(FAILED, "item", error=item.error)
            self._save()
            return item

        status = result.get("status")
        if status in ("learned", "skipped"):
            item.documentary_id = result.get("documentary_id", resolved.documentary_id)
            item.status = QueueStatus.FINISHED if status == "learned" else QueueStatus.SKIPPED
            k = result.get("knowledge")
            item.schema_version = getattr(k, "schema_version", SCHEMA_VERSION)
            item.error = ""
            self._index.record(documentary_id=item.documentary_id, video_id=resolved.video_id,
                               canonical_url=item.url, schema_version=item.schema_version)
            stats = getattr(k, "statistics", None)
            event(FINISHED, "item", doc_id=item.documentary_id, metrics={
                "shots": getattr(stats, "shot_count", 0),
                "scenes": getattr(stats, "scene_count", 0),
            })
        else:
            item.status = QueueStatus.FAILED
            item.attempts += 1
            item.error = "; ".join(e.get("message", "") for e in result.get("errors", [])) or "error"
            event(FAILED, "item", error=item.error)
        self._save()
        return item
