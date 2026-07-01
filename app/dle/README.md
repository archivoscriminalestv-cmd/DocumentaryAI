# DLE — Documentary Learning Engine

Motor de **adquisición de conocimiento**: observa documentales reales (YouTube o vídeo
local), extrae conocimiento cinematográfico **estructurado** y lo almacena de forma
**permanente y versionada** en `knowledge/`. El DLE **no genera** documentales y **no
modifica** el pipeline de generación — solo observa, analiza y almacena.

Provider-agnóstico (el origen del vídeo no afecta al análisis), determinista, serializable
y versionado. **Nunca inventa**: lo que no se puede determinar con confianza se marca
`UNKNOWN`. Si una etapa falla, registra el error y continúa.

```
Vídeo → Metadatos → (audio) → Transcripción → Escenas → Planos → Análisis cinematográfico
      → Documentary Knowledge → Persistencia (knowledge/)
```

## Módulos (`app/dle/`)

| Módulo | Responsabilidad |
|--------|-----------------|
| `models.py` | DocumentaryKnowledge, Metadata, ShotAnalysis, SceneSegment, NarrativeBlock, Statistics, Transcript, AnalysisError |
| `ffmpeg.py` | Probe (metadatos), detección de cortes (scene), extracción de fotogramas, silencios; runner inyectable + parsers puros |
| `analysis/` | `visual_style` (brillo/contraste/temp/color/luz/día-noche), `motion`, `audio`, `narration`, `cinematography` (ensambla el plano), `editing`, `pacing` |
| `segmentation/scene_detector.py` | agrupa planos en escenas (cambio de estilo visual) + bloques narrativos (UNKNOWN-safe) |
| `transcription/whisper.py` | `Transcriber` + `WhisperTranscriber` (opcional) + `NullTranscriber` (inyectable) |
| `downloader/youtube.py` | `YouTubeDownloader` (yt-dlp, runner inyectable, degrada con elegancia) |
| `providers/` | `LocalVideoProvider`, `YouTubeProvider` (resuelven el origen a un fichero local) |
| `storage/` | `statistics` (agregados), `embeddings` (vector determinista para comparar docs), `knowledge_store` (base permanente) |
| `persistence.py` | escribe documentary/scenes/shots/statistics/transcript/report |
| `orchestrator.py` | `DocumentaryLearningEngine` — pipeline que nunca rompe |

## Entrada

```bash
python -m app.cli.learn_documentary --youtube https://youtube.com/watch?v=...
python -m app.cli.learn_documentary --video documentary.mp4
python -m app.cli.learn_documentary --video doc.mp4 --scene-threshold 0.03   # fundidos suaves
```

`--scene-threshold` por defecto 0.27 (cortes duros de footage real); bájalo para vídeos
con fundidos/disoluciones.

## Análisis por plano (determinista cuando es posible)

timestamp inicio/fin, duración, escena, **movimiento** (intensidad por diferencia de
fotogramas), **iluminación**, **temperatura de color**, **contraste**, **brillo**,
**color dominante**, **audio presente**. Requieren un modelo (no disponible aún) →
`UNKNOWN`: tamaño de plano, composición, rostro, nº de personas, interior/exterior,
día/noche ambiguo, música, efectos. La narración se deriva de la transcripción si existe.

## Estadísticas + embedding

Duración media/mediana de plano, cortes/min, pacing, distribución de tamaños/movimientos/
iluminación/colores, frecuencia de primeros planos, tiempo con audio/narración/música, y
un **embedding determinista** (vector de longitud fija) para comparar documentales en el
futuro — sin ML ni aleatoriedad.

## Persistencia (permanente, versionada, no duplica)

```
knowledge/documentaries/<documentary_id>/
  documentary.json  scenes.json  shots.json  statistics.json  transcript.json  report.md
```

`documentary_id` es estable (hash del contenido local o id de YouTube). Re-ejecutar el
mismo documental es idempotente (se omite, no se duplica); `--force` re-analiza.

## Integración futura

El DLE **solo genera conocimiento**. NO se integra todavía con VIS/SDE/CME/Composer —
los próximos sprints consumirán este conocimiento.

## Decisiones arquitectónicas

Ver `docs/adr/ADR-0008-Documentary-Learning-Engine.md`.

## Resultado (dogfooding sobre el propio `documentary.mp4`)

`learn_documentary --video output/documentary/documentary.mp4 --scene-threshold 0.03` →
`knowledge/documentaries/doc_ca3e8bcdadd4/`: 31 planos, 29 escenas, 30 cortes, plano medio
2.50s (fast), 23.1 cortes/min, distribución de color/luz/movimiento, 0 errores; re-run no
duplica. Whisper/yt-dlp no instalados → transcripción `unavailable` (honesto).
