# VAI — Visual AI Director

El **Director de Fotografía** de DocumentaryAI. Convierte un `Shot` (de VIS) en la
mejor **especificación visual** posible y en un `ShotExecutionRequest` listo para
el MGL.

```
VIS (Shot) ──► VAI ──► VisualSpecification ──► PromptOptimizer ──► ShotExecutionRequest ──► MGL
```

VAI **NO** genera imágenes, **NO** llama a proveedores, **NO** toca VIS/RDA/MGL/
FFmpeg. Es **determinista** (sin IA, sin embeddings, sin red, sin APIs) e
**independiente de proveedor** (Leonardo, Flux, Ideogram, Midjourney, SDXL,
Runway, OpenAI…).

## Principio: especialistas, no un PromptBuilder gigante

Cada dimensión fotográfica es un **motor especialista** pequeño que implementa la
interfaz `VisualEngine.contribute(shot, context) -> list[str]`:

| Motor | Decide |
|-------|--------|
| `composition_engine` | rule of thirds, simetría, leading lines, foreground/background, framing, balance |
| `camera_language_engine` | traduce ShotType + camera_move a lenguaje de cine (NO cambia la cámara) |
| `lens_engine` | focal, profundidad de campo, bokeh, apertura, compresión óptica |
| `lighting_engine` | volumétrica, rim, soft/hard, god rays, chiaroscuro, bounce |
| `atmosphere_engine` | niebla, bruma, polvo, partículas, humedad |
| `color_grading_engine` | teal-orange, warm doc, cold investigative, desaturado, Kodak, IMAX |
| `realism_engine` | PBR, fotorealismo, grano, GI, sombras naturales, HDR |
| `quality_engine` | densidad/calidad técnica (8k, detalle) — términos universales |
| `negative_prompt_engine` | negativos automáticos (cartoon, cgi, watermark, flat…) |
| `prompt_optimizer` | combina todo: orden §12, dedup, limpieza |
| `visual_memory` | almacena decisiones (sin IA) para reutilización/auditoría futura |

`visual_director.py` orquesta los motores → `VisualSpecification` → request.

## Decisiones arquitectónicas (las importantes)

1. **Doble representación en el request** (`models.py`): `prompt`/`negative_prompt`
   de TEXTO (universal, cualquier proveedor) **y** `specification` ESTRUCTURADA
   (para proveedores que acepten parámetros). Así VAI no se ata a Pollinations ni
   a ninguno: el proveedor elige qué consumir.
2. **Duck-typing del Shot**: los motores leen atributos del shot por `getattr`, no
   importan tipos de VIS. VAI funciona con cualquier objeto "shot-like" → cero
   acoplamiento con VIS (que no se toca).
3. **Motores intercambiables** (interfaz `VisualEngine`): añadir/sustituir un motor
   (o una versión futura por IA con la misma firma) no obliga a tocar el director
   ni los demás motores. Pensado para crecer durante años.
4. **VAI no decide narrativa ni cámara**: respeta a VIS. `camera_language_engine`
   TRADUCE; `lighting_engine` usa `shot.lighting` como semilla. `motion`,
   `media_type` y `reuse_key` pasan intactos al request.
5. **Determinismo y variación**: `selection.rotate(options, index, offset)` da
   variación entre planos contiguos sin azar (anti-PowerPoint, ARCH-VIS-000 §13).
6. **Calidad provider-agnóstica**: `quality_engine` evita jerga de proveedor
   (`masterpiece`, `--ar`, `trending`…); usa términos universales.
7. **PromptOptimizer = orden + dedup**: una sola fuente para el formato final del
   prompt (ARCH-VIS-000 §12), separada de las decisiones de cada motor.

## Integración

- **VIS → VAI**: `VisualDirector.direct(planned_shot, VisualContext)`; el contexto
  se construye con `build_context(scene, profile, style=...)` (duck-typed).
- **VAI → MGL**: el `ShotExecutionRequest` es compatible con
  `MGL.generate_for_shot` (lee `prompt`/`media_type`/`reuse_key`). VAI ya está
  cableado en `DocumentaryAssembler` (sustituye el armado de prompt de VIS-2; VIS-2
  permanece intacto para uso directo).

## Qué NO hace (límites)
LLMs, embeddings, ML, vector DB, APIs, generación de píxeles, FFmpeg, modificar
VIS/RDA/MGL. Todo eso queda fuera por diseño.
