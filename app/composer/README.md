# Composer — Documentary Runtime (COMP-001)

Primer **runtime end-to-end** de DocumentaryAI: ejecuta el pipeline completo y produce
un **MP4 real**. El Composer **no toma decisiones** cinematográficas — ya las tomaron
CRE/CCE/ERE/VIS/VAI/SDE/VSC/VPL/ALR/CME — solo **consume sus contratos públicos y
ejecuta**.

```
VIS → VAI → SDE → VSC → CCE → VPL → ALR → CME → COMPOSER → FFmpeg → documentary.mp4
```

Para cada plano: **asset (ALR) + plan de movimiento (CME) + duración + narración → clip
MP4**. Luego: ensamblaje + transiciones + audio sincronizado (narración + música) →
`documentary.mp4`.

## Módulos (`app/composer/`)

| Módulo | Responsabilidad |
|--------|-----------------|
| `interfaces.py` | `MotionExecutor` (interfaz permanente de ejecución de movimiento) |
| `ffmpeg_motion_executor.py` | `FFmpegMotionExecutor`: ejecuta el Motion Manifest con `zoompan` (push/pan/tilt/dolly/parallax/locked/handheld + ease in/out/in-out) |
| `audio.py` | `AudioComposer`: narración ajustada a cada escena (sincronía exacta) + cama musical + mezcla voz-prioritaria |
| `transitions.py` | fade in / fade out / dissolve, decididos por el Timeline (no solapados → sincronía exacta) |
| `runtime.py` | `DocumentaryComposer`: orquesta clips → concat → mux → MP4 + `composer_manifest.json` + `composer_report.md` |
| `models.py` | `ClipResult`, `ComposerResult` |

## MotionExecutor (provider-independent)

`MotionExecutor` es la frontera permanente entre el plan (CME) y el motor que lo ejecuta.
Hoy: `FFmpegMotionExecutor`. Mañana se podrán enchufar **Runway / Veo / Kling / Luma /
Pika / OpenAI Video** implementando la misma interfaz, **sin tocar el Composer**. Los
parámetros provienen EXCLUSIVAMENTE del CME (tipo, zoom, pan, tilt, easing, amplitud).

## Sincronización audio/vídeo (exacta)

`timeline_audio == timeline_video`. La narración de cada escena se ajusta a la duración
de su escena (se acelera con `atempo` si sobra texto, se rellena con silencio si falta),
de modo que la suma total coincide con el vídeo: nunca termina a mitad ni deja silencio
final. La música va por debajo de la voz (voz prioritaria) con fundidos.

> Nota: no hay pista musical en el repo, así que el Composer **genera** una cama ambiental
> (ruido marrón filtrado, volumen bajo, con fundidos). Define `MUSIC_TRACK=<ruta>` para
> usar una pista real; la mezcla es idéntica.

## Salidas

```
output/documentary/
  documentary.mp4
  clips/ clip_001.mp4 … clip_026.mp4
  composer_manifest.json
  composer_report.md
```

El `composer_report.md` incluye duración total y por plano, duración de audio,
sincronía, transiciones, movimientos ejecutados, assets usados, cache hits, tiempo de
render, bitrate, resolución y fps.

## Decisiones arquitectónicas

Ver `docs/adr/ADR-0007-Documentary-Runtime-and-Motion-Executor.md`.

## Resultado (Coquito, primer documental end-to-end)

26 imágenes IA → 26 clips MP4 con movimiento → un único `documentary.mp4` de **78 s,
1280×720@25, H.264 + AAC**, narración sincronizada (video 78.0s == audio 78.0s), cama
musical, transiciones (fade-in + 25 dissolves + fade-out), generado **sin intervención
manual** con `python -m app.cli.generate_documentary`.
