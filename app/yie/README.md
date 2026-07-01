# YouTube Intelligence Engine (YIE) — `app/yie/`

Subsistema **aditivo, independiente, provider-agnóstico y determinista** que analiza una
URL de YouTube **antes** del DLE y almacena conocimiento permanente sobre el rendimiento
del vídeo, el canal, el SEO, la miniatura y la popularidad (inteligencia competitiva).

> No modifica VIS/CRE/CCE/ERE/VAI/VSC/VPL/ALR/SDE/CME/Composer/FFmpeg ni el DLE. No genera
> nada, no puntúa, no recomienda, no usa IA ni modelos. **`UNKNOWN` antes que inventar.**

## Pipeline
```
URL → YouTubeProvider (metadatos + miniatura) → parsers/analizadores deterministas
    → persistencia: youtube.json · seo.json · thumbnail.json · popularity.json
```
Integración con la cola (automática en `learn_queue`): **Queue → YIE → DLE** (el DLE no
cambia; el YIE corre antes, best-effort).

## Qué extrae
- **Vídeo** (`models.VideoMetadata`): video_id, title, description, publish_date, duration,
  category, language, tags, hashtags, chapters, subtitles, license, fps, resolution.
- **Canal** (`ChannelInfo`): channel_id, name, subscribers, total_views/videos, country,
  created_at, average_views (solo si hay totales reales), upload_frequency (reservado).
- **Métricas** (`VideoMetrics`): views, likes, comments, duration.
- **SEO** (`seo.py`, solo reglas): longitud/palabras del título y descripción, ratio de
  mayúsculas, números, años, preguntas, emojis, hashtags, tags, palabras significativas
  (frecuencia, sin stopwords). **Sin IA.**
- **Miniatura** (`thumbnail.py`, Pillow, solo atributos objetivos): resolución, brillo,
  contraste, saturación, temperatura de color, color dominante, % de texto (densidad de
  bordes), histogramas. **Sin detección de personas, sin CLIP, sin modelos.**
- **Popularidad** (`popularity.py`, métricas derivadas): views_per_day, likes_per_view,
  comments_per_view, engagement_rate, age_days. **Sin score con pesos arbitrarios.**

## Determinismo
Misma URL → mismos JSON. Sin `random`. La red está aislada tras `YouTubeProvider`
(inyectable; en tests, proveedores falsos → sin red). Las métricas temporales usan una
`reference_date` explícita (por defecto hoy; fija en los tests).

## Persistencia
`knowledge/documentaries/<doc_id>/{youtube,seo,thumbnail,popularity}.json` — ficheros
PROPIOS del YIE; **no se mezclan** con los del DLE. `doc_id = doc_yt_<video_id>` (misma
convención que el DLE para alinear ambos subsistemas).

## CLI
```
python -m app.cli.inspect_youtube https://www.youtube.com/watch?v=XXXXXXXX
# -> knowledge/documentaries/doc_yt_XXXXXXXX/{youtube,seo,thumbnail,popularity}.json

python -m app.cli.learn_queue
# -> Queue -> YIE -> DLE automáticamente para las URLs de YouTube
```

## Cómo añadir un proveedor nuevo
Implementa el `Protocol` `YouTubeProvider` (`fetch_metadata(url) -> dict`,
`fetch_thumbnail(raw, work_dir) -> path|None`) y pásalo a
`YouTubeIntelligenceEngine(provider=...)`. No hay que tocar parsers, orquestador ni
persistencia.

## Knowledge Synthesizer (futuro)
El DKS **no** se modifica en este sprint: el YIE solo deja preparados los contratos de
fichero/esquema. Un sprint posterior hará que el DKS consuma `youtube/seo/thumbnail/
popularity.json`.

Decisiones: ver `docs/adr/ADR-0011-YouTube-Competitive-Intelligence.md`.
