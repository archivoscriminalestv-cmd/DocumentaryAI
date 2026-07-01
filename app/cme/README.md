# CME — Cinematic Motion Engine

Director de Cámara **determinista** y **provider-agnóstico**. Transforma la secuencia de
imágenes estáticas en un **plan de movimiento** cinematográfico reproducible: decide cómo
se mueve la cámara, cuándo, hacia dónde, a qué velocidad/aceleración, con qué duración y
con qué intención narrativa.

**No** genera vídeo, **no** renderiza, **no** llama a FFmpeg ni a proveedores de IA, **no**
interpola. Solo construye un `MotionShot` por plano (intención + parámetros físicos).

Único punto de integración:

```
VIS → VAI → SDE → VSC → CME → Composer
```

El `MotionPlan` resultante puede ser ejecutado por FFmpeg, Runway, Veo, Pika, Kling,
OpenAI Video o cualquier motor futuro — nunca contiene sintaxis específica de proveedor.

## Módulos (`app/cme/`)

| Módulo | Responsabilidad |
|--------|-----------------|
| `physics.py` | Constantes físicas (m/s, °/s, %/s) + `compute_parameters` (normaliza y **acota** por identidad) |
| `motion_catalog.py` | Motion Grammar: catálogo de movimientos (familia, primary, dirección, duración, easing, energía) |
| `models.py` | `MotionFingerprint`, `MotionShot`, `MotionParameters` |
| `director.py` | `NarrativeMotionDirector`: intención narrativa → movimiento base (justificado) |
| `planner.py` | `MotionPlanner`: continuidad de escena + diversidad por LRU (sin azar) + scoring |
| `continuity.py` | Clase de escena (steady/handheld) + seguridad de identidad (límites) |
| `timeline.py` | `MotionTimeline`: start/end/duración + transiciones |
| `orchestrator.py` | `CinematicMotionEngine` + `CMEContext` + estadísticas/manifest |
| `persistence.py` | `motion_history.json` + `motion_manifest.json` + `motion_report.md` |

## Motion Grammar (catálogo)

STATIC, LOCKED, SLOW_PUSH_IN, SLOW_PULL_OUT, DOLLY_L/R, TRUCK_L/R, PAN_L/R, TILT_UP/DOWN,
CRANE_UP/DOWN, ORBIT_L/R, PARALLAX, HANDHELD_SUBTLE, HANDHELD_NERVOUS, DRONE_REVEAL,
MACRO_SLIDE, RACK_FOCUS, MICRO_BREATHING, FLOATING, REVEAL. Cada uno define familia,
estabilidad, primary físico, dirección, duración base, easing, energía y amplitud.

## Intención narrativa (no aleatoria)

El movimiento responde al rol del plano y al estilo: entrevista→push-in lento;
testimonio→locked + micro-breathing; lugar del crimen→dolly lento; reconstrucción→handheld;
fotografía histórica→paralaje 2.5D; objeto→macro slide; paisaje→drone reveal; plano
emocional→push-in; transición→static. Cada decisión queda **justificada**.

## Continuidad, personaje, diversidad

- **Continuidad de escena:** todos los planos de una escena comparten la *clase* de cámara
  (steady ó handheld); no se mezclan estilos incompatibles.
- **Personaje:** el movimiento nunca deforma rostro/proporciones/ropa/edad/identidad —
  los parámetros se acotan a límites de identidad (`physics` + `continuity.assert_identity_safe`).
- **Diversidad:** se evita repetir (nada de 26 push-in); LRU dentro de la familia + un
  *Motion Diversity Score* (0..1).

## Física (configurable)

Push-in 0.3 m/s, pan 8°/s, tilt 6°/s, zoom 4%/s, handheld 0.4°, micro-breathing 0.1°…
Todo en `physics.py`; los parámetros por plano se derivan de velocidad × duración y se
acotan (zoom ≤ 30%, pan ≤ 25°, roll ≤ 3°, traslación ≤ 0.20 de cuadro).

## Salidas

`motion_manifest.json` (shot, asset_id, motion_type, speed, duration, curve, parameters,
purpose), `motion_history.json` (plan completo) y `motion_report.md` (distribución de
movimientos, velocidad/duración media, repeticiones, diversidad, tiempo total, energía).

## Decisiones arquitectónicas

Ver `docs/adr/ADR-0006-Provider-Agnostic-Camera-Motion.md`.

## Resultado (Coquito, 26 planos)

26 `MotionShot`, **17 tipos de movimiento distintos**, diversidad **0.75**, 0 repeticiones,
energía media 0.34, timeline 78 s, identidad intacta, determinista. El Composer aún no los
ejecuta: el plan queda listo para FFmpeg / motores de IA.
