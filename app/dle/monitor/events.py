"""Eventos públicos de progreso del aprendizaje (DLE-003).

Contrato mínimo y estable que el pipeline (orquestador / job / cola) emite y que el
monitor escucha. Los campos opcionales valen ``None`` cuando el emisor no los conoce;
el monitor solo actualiza los campos presentes (los None no pisan el estado).
"""

from dataclasses import dataclass

# Tipos de evento de cada etapa del pipeline.
STARTED = "STARTED"
PROGRESS = "PROGRESS"
FINISHED = "FINISHED"
FAILED = "FAILED"

# Etapas observables (las de análisis + las sintéticas 'queue'/'item').
PIPELINE_STAGES = ("downloading", "analyzing", "learning", "storing")


@dataclass
class ProgressEvent:
    kind: str                       # STARTED | PROGRESS | FINISHED | FAILED
    stage: str = ""                 # queue | item | downloading | analyzing | learning | storing
    doc_ref: str | None = None      # URL/ruta del documental actual
    doc_id: str | None = None       # id en knowledge/
    position: int | None = None     # posición en la cola (1-indexada)
    total: int | None = None        # total a procesar
    percent: float | None = None    # 0..1 dentro de la etapa actual
    shot_index: int | None = None   # plano actual (1-indexado)
    shot_total: int | None = None
    scene_total: int | None = None
    metrics: dict | None = None     # documentaries_learned, hours_learned, kb_size_bytes, ...
    error: str | None = None


def emit(sink, event: ProgressEvent) -> None:
    """Envía un evento al sink si existe (no-op si es None)."""
    if sink is not None:
        sink(event)


def with_context(sink, **ctx):
    """Devuelve un sink que rellena los campos de contexto que el emisor dejó en None
    (p.ej. ``position``/``doc_ref`` que solo conoce la cola). No pisa valores ya puestos."""
    if sink is None:
        return None

    def _emit(event: ProgressEvent) -> None:
        for key, value in ctx.items():
            if getattr(event, key, None) is None:
                setattr(event, key, value)
        sink(event)

    return _emit
