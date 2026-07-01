# DLE Batch Learning — Automatic Learning Pipeline (DLE-002)

Convierte el DLE en un sistema capaz de aprender de **cientos o miles** de documentales
sin intervención humana. El usuario solo entrega una lista de URLs; el resto es
automático, **persistente** y **resumible**. Mantiene los principios del DLE (observe-only,
determinista, provider-agnóstico, aditivo) y **no** modifica el pipeline de generación.

```
Queue → Download → Learning → Knowledge → Statistics → Index → Finished   (todo automático)
```

## Componentes (`app/dle/queue/`)

| Módulo | Responsabilidad |
|--------|-----------------|
| `models.py` | `QueueItem` + `QueueStatus` (PENDING/DOWNLOADING/ANALYZING/LEARNING/STORING/FINISHED/FAILED/SKIPPED) |
| `store.py` | `QueueStore` — cola **persistente** (escritura atómica), dedup por URL, recuperación de trabajos interrumpidos |
| `index.py` | `KnowledgeIndex` — evita re-aprender (por documentary_id/video_id/URL + esquema) |
| `downloader.py` | Registro de fuentes desacoplado (YouTube/local hoy; Vimeo/Archive/RTVE/BBC… `register()`) |
| `job.py` | `LearningJob` — aprende UN documental; transiciones de estado; nunca rompe la cola |
| `manager.py` | `LearningQueueManager` — add/remove/pause/resume/cancel/retry/status/process_all |
| `reports.py` | `learning_report.md` + `learning_statistics.json` + `learning_history.json` |

## CLIs

```bash
python -m app.cli.queue_add urls.txt          # añade cientos de URLs (no duplica)
python -m app.cli.learn_queue                 # procesa TODA la cola automáticamente
python -m app.cli.learn_queue --limit 50      # procesa por lotes
python -m app.cli.queue_status                # progreso por documental
python -m app.cli.queue_retry [--run]         # reintenta los fallidos
python -m app.cli.queue_clear_finished        # limpia la cola (el conocimiento permanece)
```

## Garantías

- **Persistente / resumible:** cada transición de estado se guarda en disco. Si el proceso
  se cierra, al reabrir la cola continúa exactamente donde estaba; los trabajos
  interrumpidos (en vuelo) vuelven a PENDING y se reanudan. Nunca se pierde trabajo.
- **Nunca aprende dos veces:** antes de descargar se comprueba el índice (id de vídeo / URL
  / hash). Si ya existe con el esquema actual → `SKIPPED` (sin descargar).
- **Aprendizaje incremental (diseño):** si el documental fue aprendido con un esquema
  anterior y existe uno nuevo, se re-aprende; el índice gatea por versión de esquema. (Con
  esquema 1.0 único, hoy siempre se omite lo idéntico.)
- **Descarga y aprendizaje desacoplados:** nuevas fuentes se añaden con `register()` sin
  tocar el motor; cada documental es un `LearningJob` que el manager ejecuta.
- **Tolerante a fallos:** un documental que falla se marca `FAILED` (con su error) y la cola
  continúa; `queue_retry` lo reintenta. Límite de intentos configurable.

## Decisiones arquitectónicas

Ver `docs/adr/ADR-0009-Automatic-Batch-Learning-Pipeline.md`.

## Demostración (lotes reales, locales)

Cola con 3 vídeos → `learn_queue` procesó los 3 automáticamente (33 planos, 31 escenas);
re-ejecutar procesó 0 (sin duplicar). Persistencia verificada: un manager nuevo sobre la
misma `learning_queue.json` reanuda lo pendiente.
