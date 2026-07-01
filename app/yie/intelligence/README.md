# Competitive Intelligence & Audience Analytics (YIE-002) — `app/yie/intelligence/`

Evoluciona el YIE en un sistema de **inteligencia competitiva** de YouTube: análisis
profundo de canal, audiencia, engagement, SEO extendido y miniatura extendida, con una
capa de **proveedores de enriquecimiento opcionales** y un `provider_coverage.json`
auditable.

> Aditivo, determinista, sin IA/modelos/scoring/recomendaciones. `UNKNOWN` antes que
> estimar. Reutiliza las funciones puras del YIE-001 (no las modifica) y NO toca el DLE
> ni el DKS. Ver `docs/adr/ADR-0012`.

## Arquitectura
```
URL → CompetitiveIntelligenceEngine → providers (yt-dlp + enriquecimiento opcional) → knowledge
                                       ├─ yt-dlp / YouTube metadata   (base)
                                       ├─ vidIQ                       (opcional, hoy UNKNOWN)
                                       └─ SocialBlade/GoogleTrends/Wayback/TubeBuddy (contratos)
```
Cada proveedor es **independiente y opcional**: si no está disponible → `UNKNOWN` y se
continúa. Nunca navegador, nunca HTML, nunca rompe el pipeline.

## Ficheros que escribe (por documental)
Reutiliza/produce los del YIE-001 sin cambiarlos (`youtube/seo/thumbnail/popularity.json`)
y añade:
- **channel.json** — `ChannelIntelligence`: subs, total vídeos/vistas, país, creación,
  edad del canal, verificado, artista oficial, custom URL, keywords, playlists, y
  derivadas (average_views/video, uploads/año, uploads/mes).
- **audience.json** — `AudienceMetrics`: views/subscriber, subscribers/view,
  channel_views/subscriber, average_views/video.
- **engagement.json** — `EngagementMetrics`: views/day, likes/view, comments/view,
  engagement_rate, like_velocity, comment_velocity.
- **competitive.json** — registro consolidado (métricas + engagement + audiencia + canal
  + SEO extendido + miniatura extendida + flags). Es el registro que minará el DKS.
- **provider_coverage.json** — auditoría: de qué proveedor vino cada campo (o `UNKNOWN`),
  proveedores disponibles/no disponibles y ratio de cobertura.

## Métricas derivadas (solo fórmulas)
views/day, likes/view, comments/view, subscribers/view, views/subscriber, uploads/year,
uploads/month, views/video, like_velocity, comment_velocity, engagement_rate. Nada se
inventa: si falta un insumo, la derivada es `None`.

## Miniatura extendida (Pillow, objetivo)
aspect ratio, brillo, contraste, saturación media, temperatura de color, color dominante,
**paleta de color**, densidad de bordes, % de texto (densidad de bordes), bordes en el
margen exterior, histogramas. **Sin personas, sin emociones, sin CLIP, sin IA.** La imagen
se analiza en un temporal y se descarta.

## SEO extendido (reglas)
longitudes (título/descripción), nº de palabras, primera línea, enlaces, hashtags, tags,
capítulos, ratio de stopwords, repetición de palabra clave, densidad de keywords, pinned
comment (si lo aporta un proveedor).

## Cómo añadir un proveedor de enriquecimiento
Implementa `EnrichmentProvider` (`providers/base.py`): `name`, `available()`,
`fetch(video_id, raw) -> dict` (claves canónicas públicas). Pásalo en
`CompetitiveIntelligenceEngine(enrichment_providers=[...])`. vidIQ/SocialBlade/… ya tienen
su contrato listo; activar uno es inyectar su `client` oficial.

## Integración
`learn_queue` cablea automáticamente `CompetitiveIntelligenceEngine` como `intelligence=`
del `LearningQueueManager`: **Queue → YIE → DLE** (best-effort; el DLE no cambia).
Determinista (misma URL → mismos JSON; `reference_date` inyectable).
