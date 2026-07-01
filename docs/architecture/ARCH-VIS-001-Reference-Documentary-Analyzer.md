# ARCH-VIS-001 — Reference Documentary Analyzer (RDA)

> Estado: **Diseñado e implementado** (`app/rda/`). Motor que aprende la
> GRAMÁTICA audiovisual de cualquier vídeo de referencia y la guarda como
> conocimiento reutilizable que alimenta ARCH-VIS-000 (Cinematic Language Spec)
> y el futuro Visual Intelligence System (VIS). Aditivo: no toca nada existente.

---

## 1. Propósito y límites

El RDA **no está ligado a un vídeo concreto**: analiza cualquier referencia
accesible (YouTube, MP4 local, URL) y extrae **solo cómo está construida**
(montaje, ritmo, luz, color, movimiento). El objetivo es **aprender el lenguaje
visual**, no copiar el documental.

**Línea roja (MUST NOT):** el RDA NO extrae contenido narrativo. Sin
transcripción, sin reconocimiento de objetos/personas, sin descripción del
relato. Solo **estadísticas visuales agregadas**. No se retiene ningún fotograma
del original: los frames muestreados se procesan en un directorio temporal y se
**borran**; solo persiste el perfil numérico.

---

## 2. Posición en la arquitectura

```
Vídeo de referencia ──► RDA ──► CinematicProfile ──► ReferenceLibrary (output/rda/*.json)
 (YouTube/MP4/URL)                (gramática)              │
                                                          ▼
                                        Conocimiento reutilizable que CALIBRA
                                        ARCH-VIS-000 y los presets del VIS
```

El RDA es una **capacidad transversal de aprendizaje**, paralela al pipeline de
producción. No genera vídeo; produce **conocimiento**.

---

## 3. Módulos (`app/rda/`)

| Módulo | Responsabilidad |
|--------|-----------------|
| `models.py` | `FrameFeatures`, `ShotProfile`, `CinematicProfile` (dataclasses puras, JSON). |
| `analysis.py` | **Lógica pura**: detección de cortes (`detect_boundaries`), agregación por plano y mapeo a vocabulario (`pacing_tier`, `lighting_tendency`, `color_temperature`, `saturation_tendency`, `movement_tendency`, `variety_label`) → `build_profile`. Sin ffmpeg ni red. |
| `frame_extractor.py` | `FfmpegFrameExtractor`: muestrea N fps a baja resolución (temporal) y calcula `FrameFeatures` con Pillow; borra los frames. |
| `sources.py` | `resolve_source`: fichero local (directo) o URL (descarga temporal vía `yt-dlp` opcional). Devuelve `(ruta, tipo, cleanup)`. |
| `library.py` | `ReferenceLibrary`: persiste/lista/carga `CinematicProfile` como JSON (la base de conocimiento). |
| `analyzer.py` | `ReferenceDocumentaryAnalyzer`: fachada `analyze(reference) → CinematicProfile`. |
| `app/cli/analyze_reference.py` | Comando único: `python -m app.cli.analyze_reference "<url\|mp4>"`. |

---

## 4. Flujo

```
referencia
  │  sources.resolve_source            (local | yt-dlp → temp)
  ▼
ruta local
  │  FfmpegFrameExtractor.probe        (duración, resolución, fps)
  │  FfmpegFrameExtractor.extract      (fps↓, scale↓ → FrameFeatures[]; borra frames)
  ▼
FrameFeatures[]
  │  analysis.detect_boundaries        (cortes por diferencia de huella 8x8)
  │  analysis.build_profile            (ShotProfile[] + agregados + mapeo vocab)
  ▼
CinematicProfile  ──►  ReferenceLibrary.save  (output/rda/<slug>.json)
```

---

## 5. Qué mide (gramática, no contenido)

Por **fotograma** (`FrameFeatures`): brillo (luma), contraste (σ luma), calidez
(R−B), colorfulness (Hasler-Süsstrunk), huella gris 8×8 (para diferencias).

Por **plano** (`ShotProfile`, entre cortes): duración, brillo/contraste/calidez/
colorfulness medios, **motion** (diferencia media intra-plano → movimiento).

Por **referencia** (`CinematicProfile`):

- **Montaje/ritmo:** nº de planos, ASL (avg shot length), mediana/min/max, σ,
  cuts/min, `pacing_tier` (§6) y `shot_length_variety` (§6.2/§13.4).
- **Iluminación:** brillo/contraste medios → `lighting_tendency` (§4).
- **Color/grade:** calidez y colorfulness → `color_temperature` + `saturation_tendency` (§12).
- **Cámara:** motion medio → `movement_tendency` (§2/§11).
- **Composición:** aspect ratio (§5).
- `grammar_notes` (frases legibles) y `spec_alignment` (mapeo a secciones de
  ARCH-VIS-000).

Detección de cortes: diferencia normalizada (0–1) de la huella 8×8 entre frames
consecutivos; ≥ umbral (`CUT_THRESHOLD=0.30`, ajustable) = corte duro. Detecta
cortes duros con fiabilidad; disolvencias largas se suavizan (límite conocido).

---

## 6. Cómo alimenta ARCH-VIS-000 y el VIS

1. **Calibración de umbrales:** los rangos de la spec (pacing tiers, low/high-key,
   warm/cool, dynamic/static) se afinan con perfiles reales de canales de
   referencia (`spec_alignment` ya enlaza cada métrica con su sección).
2. **Presets de estilo del VIS:** una `CinematicProfile` (o la media de varias de
   un canal) se traduce en defaults del `StyleEngine`/`Rule*` del VIS (ritmo,
   grade, tendencia de movimiento) → el look "tipo Fern/Johnny Harris" deja de
   ser subjetivo y pasa a ser medible.
3. **Banco acumulable:** la `ReferenceLibrary` crece con cada referencia; varias
   referencias → estadística agregada del estilo objetivo.

> Nota: el RDA **describe**; no decide. La traducción perfil→reglas del VIS es un
> paso posterior y explícito (futuro), no automático.

---

## 7. Dependencias y degradación

- **ffmpeg** vía `imageio-ffmpeg` (ya presente) — frames + probe.
- **Pillow** (ya presente) — métricas por frame.
- **yt-dlp** (opcional) — solo para URLs; si falta, error claro pidiendo MP4 local.
- Sin red para ficheros locales. Sin IA, sin embeddings, sin ML.

---

## 8. Aditividad / no rotura

Paquete nuevo `app/rda/` + un CLI nuevo. No modifica dominio, MGL, providers,
ReuseEngine, StyleEngine, FFmpeg pipeline, ni el VIS. No retiene contenido del
vídeo. La suite existente no cambia.

---

## 9. Validación (primer caso de estudio: el tráiler)

El motor está probado con vídeo sintético (segmentos de color → cortes/brillo
detectados) y unitarios deterministas. Para el **tráiler** que se proporcione:

```
python -m app.cli.analyze_reference "<URL del tráiler | tráiler.mp4>"
```

produce su `CinematicProfile` (ASL, pacing, grade, movimiento, variedad…) en
`output/rda/` y las `grammar_notes`. El objetivo: **aprender su gramática**, no
su contenido. (URLs requieren `pip install yt-dlp`; un MP4 local funciona sin nada
más.)

---

## 10. Límites conocidos / futuro

- Cortes: fiable en cortes duros; disolvencias/fundidos largos se infravaloran.
- Movimiento: heurístico (diferencia de frames); no distingue tipo de movimiento
  (pan vs zoom) — eso es trabajo futuro (flujo óptico).
- Audio: v1 es **solo visual**; el ritmo musical/energía (sin ASR, sin contenido)
  es una extensión futura.
- Calibración: los umbrales son iniciales; se ajustarán con referencias reales.
```
