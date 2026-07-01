# VSC — Visual Scene Compiler

Puente entre **planificación** (VIS/VAI) y **renderizado** (proveedor real, próximo
sprint). Convierte un `ShotExecutionRequest` (VAI) + un `SceneVisualContext` en un
`VisualGenerationRequest` **normalizado e independiente del proveedor**.

```
VIS → VAI (ShotExecutionRequest) ─┐
                                  ├─► VisualSceneCompiler ─► VisualGenerationRequest ─► VisualProvider (futuro) ─► GeneratedAsset
SceneVisualContext (continuidad) ─┘                              (provider-agnóstico)        + AssetCache (reuse_key)
```

El VSC **no** conoce a Imagen/Flux/Midjourney/SDXL/Runway/Veo/Pika: su
responsabilidad termina cuando existe una petición de generación normalizada.

## Piezas (`app/vsc/`)

| Módulo | Responsabilidad |
|--------|-----------------|
| `models.py` | `GlobalStyle`, `SceneVisualContext` (frozen/inmutable), `VisualGenerationRequest` (serializable), `GeneratedAsset` |
| `compiler.py` | `VisualSceneCompiler.compile(shot_request, scene, global_style)` — prompt por capas + continuidad + motion_hint + seed + reuse |
| `provider.py` | `VisualProvider` (Protocol) + `MockVisualProvider` + `CachingVisualProvider` |
| `cache.py` | `AssetCache` — reutiliza por `reuse_key` |
| `context_adapter.py` | `to_vai_context(scene, subject)` — coherencia escena↔plano |

## Compilación por capas

`GLOBAL STYLE → SCENE STYLE → SHOT STYLE → payload`. El prompt final es una sola
descripción coherente (no fragmentos sueltos), y además se exponen las 3 capas por
separado (`global_style`, `scene_style`, `shot_style`) para que cualquier adaptador
las recomponga.

## Continuidad (lo importante)

`SceneVisualContext` es la **fuente de verdad de continuidad**: cámara, lente,
clima, paleta, iluminación, localización, estación y hora son IDÉNTICAS en todos
los planos de la escena. El plano solo aporta variación (sujeto, composición,
lenguaje de cámara) vía VAI. Ningún plano cambia clima/cámara/paleta salvo override
de la escena.

## Caché de assets

`AssetCache` + `CachingVisualProvider` reutilizan por `reuse_key` (p.ej.
`corner_finestrelles_almassora`): una localización recurrente se genera una vez y
se reutiliza. `reuse_key` vacío ⇒ siempre único (anti-colapso).

## Independencia de proveedor

`VisualGenerationRequest` lleva texto universal (`prompt`/`negative_prompt`) + campos
estructurados (camera/lens/lighting/composition/color/environment/subject/
provider_constraints/seed/motion_hint). `VisualProvider.generate(request)` es la
interfaz neutra; los adaptadores reales llegan en el próximo sprint.

## Motion (placeholder)

No se genera movimiento: cada request lleva `motion_hint`
(`slow_push_in`/`parallax`/`locked`/`tracking_left`/…) que consumirá el futuro
Motion Engine.

## Decisiones de diseño
- **No reemplaza** VIS/VAI/MGL/Composer: es un subsistema nuevo y aditivo.
- **Frozen** `SceneVisualContext` (inmutable) para garantizar continuidad.
- **Doble representación** (texto + estructura) para soportar cualquier proveedor.
- **Determinista**: sin IA, sin red, sin APIs. Seeds deterministas por estrategia.

## Ejemplo
`python -m app.cli.compile_coquito` compila el documental "Coquito" en
`VisualGenerationRequest` por plano (continuidad por escena) y demuestra la caché
de localización. Su salida es la entrada del próximo sprint (proveedor real).
