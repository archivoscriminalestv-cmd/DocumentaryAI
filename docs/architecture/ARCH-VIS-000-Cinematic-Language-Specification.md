# ARCH-VIS-000 — Cinematic Language Specification

> **La biblia visual de DocumentaryAI.** Define el lenguaje cinematográfico que
> el Visual Intelligence System (VIS) seguirá de forma ESTRICTA. Documento
> **independiente de implementación**: sin código, sin APIs, sin pipeline.
>
> Referencia de calidad ("north star"): MagnatesMedia, Johnny Harris, Fern,
> RealLifeLore, Neo, James Jani. Objetivo: documentales que parezcan **dirigidos**,
> no presentaciones.
>
> Lenguaje normativo: **MUST** (obligatorio), **SHOULD** (recomendado salvo
> justificación), **MUST NOT** (prohibido). El VIS debe poder citar la regla que
> aplica en cada decisión.

---

## 0. Cómo se usa esta especificación

Cada sección define un **vocabulario controlado** y unas **reglas**. El VIS
traduce esas reglas a los campos del `Shot` (ver ARCH-VIS):

| Sección de esta spec | Campo(s) de `Shot` que gobierna |
|----------------------|---------------------------------|
| §1 Shot taxonomy | `shot_type` |
| §2 Camera language / §11 Movement | `camera` (`CameraSpec`) |
| §3 Lens language | dentro de `prompt` (óptica) |
| §4 Lighting language | `lighting` + `prompt` |
| §5 Composition | `prompt` (encuadre) |
| §6 Visual pacing | `duration` |
| §7 Emotional grammar | modula §2/§3/§4/§6 según `tone`/`emphasis` |
| §8 Editing grammar / §9 Transitions | orden de `shots` + metadato de transición |
| §10 Asset selection | `asset_type` + `provider_hint` |
| §12 Prompt grammar | `prompt` |
| §13 Anti-repetición | invariantes sobre la `VisualTimeline` |
| §14 Visual storytelling | reglas transversales de coherencia |

Entradas que el VIS ya tiene del resto del sistema y que esta spec usa como
señales: `tone` (DirectorService C-08: `investigative | explanatory | dramatic |
neutral | conclusive`), `emphasis` (0–1), `relationship_type` (Knowledge:
`causal | temporal | hierarchical | geographical | associative`), y el `style`
global del vídeo (StyleEngine: `documentary | cinematic | youtube_documentary |
nature_doc | investigative_report`).

---

## 1. Shot Taxonomy (tipos de plano)

Vocabulario canónico (alineado con `ShotType`):

- **ESTABLISHING** — sitúa el contexto/lugar. Abre secuencias.
- **WIDE** — escala y relación entre elementos.
- **MEDIUM** — sujeto en su entorno; plano "de trabajo".
- **CLOSEUP / DETAIL** — un detalle significativo; intimidad o énfasis.
- **ACTION** — algo se mueve o sucede.
- **IMPACT** — el momento clave / clímax de la escena.
- **AFTERMATH** — la consecuencia, el "después".
- **REACTION** — efecto humano/emocional.
- **MAP** — geografía, rutas, escalas espaciales (clave estilo RealLifeLore).
- **INFOGRAPHIC** — cifra, dato, diagrama, comparación.
- **TRANSITION** — plano puente entre ideas.

Reglas:

- **R1.1 (MUST)** Una escena se cuenta como **secuencia de planos**, nunca como un
  único plano sostenido. Mínimo **3** planos por escena con narración no trivial.
- **R1.2 (MUST)** Toda secuencia debe contener al menos un plano de **contexto**
  (ESTABLISHING/WIDE/MAP) y al menos un plano de **detalle/énfasis**
  (CLOSEUP/DETAIL/IMPACT/INFOGRAPHIC). Variedad de escala obligatoria.
- **R1.3 (SHOULD)** Abrir con contexto, cerrar con síntesis (AFTERMATH/WIDE/
  REACTION). El clímax (IMPACT) va en el tercio central-final, no al inicio.
- **R1.4 (MUST NOT)** Dos planos consecutivos del **mismo `shot_type`** con el
  mismo encuadre (ver §13).

---

## 2. Camera Language (gramática de cámara)

Vocabulario canónico (alineado con `CameraMove`): `static, push_in, pull_out,
zoom_in, zoom_out, pan_left, pan_right, tilt_up, tilt_down, drone, tracking,
parallax, orbital, ken_burns`.

Significado **semántico** (qué comunica cada movimiento):

| Movimiento | Comunica | Úsese en |
|-----------|----------|----------|
| `push_in` | acercamiento emocional, revelación, tensión creciente | IMPACT, CLOSEUP, REACTION |
| `pull_out` | revelación de contexto, conclusión, "soltar" | AFTERMATH, cierre |
| `parallax` | profundidad sobre imagen fija (separa capas) | stills 2D (Johnny Harris look) |
| `drone` / orbital | escala, grandiosidad, geografía | ESTABLISHING, MAP, WIDE |
| `tracking` | seguir la acción, energía | ACTION |
| `pan` / `tilt` | recorrer un espacio/relación, revelar | WIDE, MAP, INFOGRAPHIC |
| `ken_burns` | vida mínima sobre archivo/foto | fotos históricas, stock |
| `static` | gravedad, foco total en el contenido | dato grave, retrato, cita |

Reglas:

- **R2.1 (MUST)** **Ningún plano es 100 % estático por defecto.** `static` solo
  por decisión deliberada (gravedad/cita/dato). El "PowerPoint" (imagen fija sin
  movimiento) está **prohibido**.
- **R2.2 (MUST)** El movimiento debe ser **lento y motivado** salvo en ACTION/
  IMPACT. Velocidad por defecto: 0.5–1.0 (lenta); 1.2–1.6 solo en acción/impacto.
- **R2.3 (SHOULD)** El movimiento "entra" hacia el punto de interés (push-in a
  un sujeto, no a una zona vacía).
- **R2.4 (MUST NOT)** Repetir el mismo movimiento en planos consecutivos (§13).
- **R2.5 (SHOULD)** Imágenes 2D/fijas → preferir `parallax`/`ken_burns`/`push_in`;
  vídeo nativo → movimiento real de cámara (`tracking`/`drone`/`orbital`).

---

## 3. Lens Language (óptica)

La óptica forma parte del **prompt** (§12) y comunica tanto como el encuadre.

Vocabulario y semántica:

| Óptica | Efecto | Úsese en |
|--------|--------|----------|
| `ultra-wide 14–24mm` | inmersión, escala, drama espacial | ESTABLISHING, MAP, paisaje |
| `wide 35mm` | "look documental" natural, versátil | MEDIUM por defecto |
| `normal 50mm` | perspectiva humana, neutral | retrato, testimonio |
| `tele 85–135mm` | compresión, aislar sujeto, intimidad | CLOSEUP, REACTION |
| `super-tele 200mm+` | compresión extrema, vigilancia/distancia | tensión, observación |
| `macro` | textura, detalle físico (evidencia) | DETAIL/INFOGRAPHIC físico |

Profundidad de campo (DoF):

- **R3.1 (SHOULD)** Sujeto destacado → **shallow depth of field** (bokeh) para
  separarlo del fondo. Contexto/escala → **deep focus**.
- **R3.2 (MUST)** La óptica debe ser **coherente con el `shot_type`**: no usar
  macro para un establishing ni ultra-wide para un detalle íntimo.
- **R3.3 (SHOULD)** Variar la distancia focal entre planos contiguos (§13): es la
  herramienta principal contra la monotonía visual.

---

## 4. Lighting Language (iluminación)

Vocabulario base: `soft natural`, `golden hour`, `blue hour`, `overcast diffuse`,
`hard directional`, `low-key chiaroscuro`, `high-key`, `volumetric / god rays`,
`rim / backlight`, `practical lights`, `moonlight / nocturne`.

Reglas:

- **R4.1 (MUST)** La luz se elige por **emoción** (§7), no al azar. Cada plano
  declara su intención lumínica en `lighting`.
- **R4.2 (SHOULD)** Coherencia de luz dentro de una misma secuencia (continuidad
  de hora del día / dirección de luz) salvo salto temporal narrativo.
- **R4.3 (SHOULD)** Drama/tensión → `low-key chiaroscuro`, `hard directional`,
  `rim light`. Esperanza/apertura → `golden hour`, `soft natural`, `high-key`.
  Gravedad/análisis → `overcast diffuse`, `practical`.
- **R4.4 (SHOULD)** `volumetric lighting` para escala y espectacularidad (espacio,
  catedrales, niebla) — con moderación, no en cada plano.

---

## 5. Composition Rules (composición)

- **R5.1 (MUST)** Aplicar una guía compositiva explícita por plano: `rule of
  thirds`, `centered/symmetry`, `leading lines`, `frame within a frame`,
  `negative space`, `foreground occlusion` (capas).
- **R5.2 (SHOULD)** **Profundidad por capas** (primer término / sujeto / fondo):
  habilita parallax y da look cinematográfico (Johnny Harris).
- **R5.3 (SHOULD)** `negative space` orientado hacia donde "mira" o se moverá el
  sujeto (espacio de mirada / espacio de acción).
- **R5.4 (SHOULD)** Simetría/centrado para gravedad o autoridad (instituciones,
  monumentos, datos); thirds para naturalidad.
- **R5.5 (MUST)** Relación de aspecto **16:9**, encuadre horizontal, calidad
  "broadcast". (Reels/9:16 quedan fuera de esta spec.)

---

## 6. Visual Pacing (ritmo)

El ritmo se controla con la **duración** de cada plano (`duration`).

Duraciones base por tipo (orientativas; el VIS las re-escala al audio, §8):

| shot_type | duración base |
|-----------|---------------|
| ESTABLISHING / WIDE / MAP | 4–6 s |
| MEDIUM | 3–4 s |
| CLOSEUP / DETAIL | 2–3 s |
| ACTION | 2–4 s |
| IMPACT | 4–5 s (puede sostenerse para peso) |
| AFTERMATH | 3–4 s |
| INFOGRAPHIC | 4–6 s (legibilidad) |
| TRANSITION | 0.5–1.5 s |

Reglas:

- **R6.1 (MUST)** El ritmo se modula por `tone`/`emphasis`: investigación/tensión
  → planos **más cortos** (corte rápido); reflexión/conclusión → planos **más
  largos**. `emphasis` alto alarga el IMPACT.
- **R6.2 (SHOULD)** Variar duraciones entre planos contiguos (evitar metrónomo:
  4-4-4-4 está prohibido por monótono, §13).
- **R6.3 (MUST)** Ningún plano sin movimiento puede durar > **6 s** (genera
  sensación de imagen congelada). Con movimiento, máximo recomendado 8 s.
- **R6.4 (SHOULD)** Acelerar hacia el clímax (planos progresivamente más cortos),
  desacelerar en el cierre.

---

## 7. Emotional Grammar (gramática emocional)

La emoción de la escena (derivada de `tone` y del contenido) **modula** óptica,
luz, cámara y ritmo de forma coherente:

| Emoción / `tone` | Cámara | Óptica | Luz | Ritmo |
|------------------|--------|--------|-----|-------|
| `investigative` (tensión, misterio) | push_in lento, super-tele estático | tele/compresión | low-key, hard | cortes cortos |
| `dramatic` (clímax, peso) | push_in fuerte, orbital | wide o tele | chiaroscuro, rim | IMPACT largo, resto corto |
| `explanatory` (claridad) | parallax, pan, ken_burns | 35–50mm | soft/diffuse | medio, legible |
| `neutral` (contexto) | drone, pull_out | wide/ultra-wide | natural | medio |
| `conclusive` (cierre, resonancia) | pull_out lento | wide | golden hour | planos largos |

- **R7.1 (MUST)** Las cuatro dimensiones (cámara/óptica/luz/ritmo) deben ser
  **coherentes** con la emoción: nada de un push-in tenso con luz high-key alegre.
- **R7.2 (SHOULD)** Construir un **arco emocional** a lo largo del vídeo (no plano):
  apertura → escalada → clímax → resolución (ligado a §8).

---

## 8. Documentary Editing Grammar (montaje)

- **R8.1 (MUST)** **Sincronía narración↔imagen**: la suma de duraciones de los
  planos de una escena se ajusta a la duración del audio de esa escena. La imagen
  cambia con las ideas, no por reloj.
- **R8.2 (MUST)** **B-roll sobre narración**: la voz guía; los planos ilustran y
  refuerzan, no compiten. Un plano nuevo por **idea/beat**, no por frase fija.
- **R8.3 (SHOULD)** **Match on action / continuidad**: planos contiguos conectan
  por movimiento, dirección o tema; evitar saltos arbitrarios.
- **R8.4 (SHOULD)** **Regla de los 180°** y continuidad direccional cuando haya
  un eje de acción/recorrido (mapas, viajes).
- **R8.5 (SHOULD)** Insertar planos de **respiro** (WIDE/AFTERMATH) tras momentos
  intensos para no fatigar.
- **R8.6 (MUST)** El primer plano del vídeo es un **hook** visual fuerte
  (ESTABLISHING espectacular o IMPACT/pregunta), nunca un plano débil.

---

## 9. Transition Rules (transiciones)

Vocabulario: `hard cut` (por defecto), `cross-dissolve`, `match cut`,
`whip pan / motion transition`, `morph/zoom transition`, `fade to/from black`,
`speed ramp`.

Selección por contexto (ligada al `relationship_type` del Knowledge y al montaje):

| Contexto | Transición |
|----------|-----------|
| Dentro de una secuencia (mismo tema) | `hard cut` |
| Salto temporal (`temporal`) | `cross-dissolve` o `fade` |
| Relación causal (`causal`) | `match cut` / `motion transition` (causa→efecto) |
| Cambio de lugar (`geographical`) | `whip pan` / `zoom transition` |
| Cambio de capítulo/idea mayor | `fade to black` |
| Energía/acción | `speed ramp` / `whip pan` |

Reglas:

- **R9.1 (MUST)** El **corte directo** es la transición por defecto. Los efectos
  se usan con **intención**, no de adorno.
- **R9.2 (MUST NOT)** Transiciones llamativas (zoom/whip/star-wipe) de forma
  repetida o decorativa: marcan amateur.
- **R9.3 (SHOULD)** `fade to/from black` reservado para inicio, cierre y saltos de
  capítulo.

---

## 10. Asset Selection Rules (elección de fuente)

Vocabulario (alineado con `AssetType`): `ai_image`, `ai_video`, `reusable`,
`stock`, `animation`.

Heurística de selección por tipo de plano (orientativa; decide `AssetStrategy`):

| Necesidad del plano | Fuente preferida |
|---------------------|------------------|
| Concepto/visual imposible o estilizado (espacio, histórico recreado) | `ai_image` (+ parallax) o `ai_video` |
| Acción/movimiento real | `ai_video` (cuando exista) |
| Sujeto ya visto antes en el vídeo | `reusable` (por `reuse_key`) |
| Realidad concreta disponible (naturaleza, ciudades, gente) | `stock` |
| Mapa / dato / diagrama / comparación | `animation` / `infographic` |

Reglas:

- **R10.1 (MUST)** Elegir **la mejor fuente disponible** para la intención, no
  siempre la misma. Un documental mezcla fuentes (IA + stock + mapas + archivo).
- **R10.2 (MUST)** `reusable` solo si el **sujeto** coincide (mismo `reuse_key`
  por sujeto, §13/§14), nunca por coincidencia de prompt estilizado.
- **R10.3 (SHOULD)** MAP/INFOGRAPHIC → animación/diagrama, no foto genérica.
- **R10.4 (MUST)** Si la fuente preferida no está disponible, degradar con un
  **fallback definido** (p.ej. ai_video→ai_image+parallax), nunca dejar el plano vacío.

---

## 11. Camera Movement Rules (reglas de movimiento)

Refina §2 con parámetros (`CameraSpec.speed`, `intensity`):

- **R11.1 (MUST)** Movimiento **continuo y suave** (ease-in/ease-out); sin tirones.
- **R11.2 (MUST)** Una sola **idea de movimiento por plano** (no combinar
  push-in + pan + tilt en el mismo plano).
- **R11.3 (SHOULD)** Amplitud `intensity` moderada (0.3–0.6) por defecto; alta
  (0.7–1.0) solo en IMPACT/ACTION.
- **R11.4 (SHOULD)** Dirección del movimiento **coherente** con el montaje (§8.3):
  encadenar movimientos que fluyen (p.ej. pull-out → push-in del siguiente).
- **R11.5 (MUST NOT)** Movimiento sin motivación (mover por mover) ni movimiento
  que aleje del punto de interés.

---

## 12. Cinematic Prompt Grammar (gramática del prompt)

Los prompts describen **fotografía**, no objetos. Orden canónico de componentes:

```
[shot_type/encuadre] + [sujeto + acción] + [entorno] + [óptica/lente + DoF] +
[iluminación] + [paleta/color grade] + [estilo/medio] + [calidad/atmósfera]
```

Ejemplo (IMPACT, asteroide):

```
Ultra realistic cinematic wide shot of a massive asteroid striking Earth's
surface, debris and shockwave, seen from low orbit, ultra-wide 18mm deep focus,
hard directional light with volumetric god rays, teal-and-amber color grade,
IMAX documentary photography, hyper-detailed, atmospheric perspective, 8k
```

Reglas:

- **R12.1 (MUST)** Todo prompt incluye: **encuadre, óptica, iluminación, estilo,
  calidad/atmósfera**. Un prompt sin óptica ni luz está **prohibido**.
- **R12.2 (MUST)** Describir **cómo se fotografía** (lente, luz, grade, perspectiva),
  no solo **qué hay**.
- **R12.3 (SHOULD)** Incluir un **color grade** coherente con el `style` global
  (consistencia del vídeo) y con la emoción (§7).
- **R12.4 (MUST)** **Negative prompt / anti-clichés** (§13): excluir
  `text, watermark, logo, low quality, deformed, oversaturated, stock-photo look,
  generic clipart`.
- **R12.5 (SHOULD)** Coherencia de sujeto entre planos del mismo elemento
  (descriptores estables del sujeto → mismo `reuse_key`), variando solo encuadre/
  óptica/luz.
- **R12.6 (MUST NOT)** Prompts genéricos de una sola frase ("an asteroid hitting
  earth"). El mínimo es la gramática completa de R12.1.

---

## 13. Anti-Repetition Rules (evitar monotonía)

Invariantes que el VIS DEBE cumplir sobre la `VisualTimeline` (y entre escenas):

- **R13.1 (MUST NOT)** Dos planos **consecutivos** con el mismo `shot_type`.
- **R13.2 (MUST NOT)** Dos planos **consecutivos** con el mismo `CameraMove`.
- **R13.3 (MUST)** Variar la **óptica/escala** entre planos contiguos (alternar
  wide ↔ tele).
- **R13.4 (MUST NOT)** Más de **2** planos seguidos con la **misma duración**
  (evitar ritmo metrónomo).
- **R13.5 (MUST)** **Una imagen ≠ una escena entera**: prohibido reutilizar el
  mismo asset para una escena completa. La reutilización (`reuse_key`) es por
  **sujeto puntual** que reaparece, no por relleno.
- **R13.6 (SHOULD)** Diversidad de **fuentes** (`asset_type`) a lo largo del vídeo
  (no todo `ai_image`).
- **R13.7 (SHOULD)** Variedad de **composición y luz** entre planos del mismo
  sujeto para que no parezcan la misma toma.

> Estas reglas **resuelven explícitamente** el problema detectado de "una imagen
> estática durante toda la narración" y el colapso reuse+style.

---

## 14. Visual Storytelling Rules (narrativa visual)

- **R14.1 (MUST)** **Mostrar, no ilustrar literalmente.** La imagen aporta
  significado/emoción, no es un pictograma de la palabra narrada.
- **R14.2 (MUST)** **Coherencia visual del vídeo**: un `style` global y una paleta
  consistente (consistencia ≠ repetir el mismo plano).
- **R14.3 (SHOULD)** **Motivos recurrentes**: un sujeto/símbolo que reaparece
  hilando el relato (uso legítimo de `reusable` por sujeto).
- **R14.4 (SHOULD)** **Escala y contraste**: alternar lo macro (detalle) y lo
  cósmico (escala) para dar amplitud (estilo RealLifeLore/Fern).
- **R14.5 (MUST)** **Causa→efecto visual**: en relaciones causales, encadenar el
  plano de la causa y el del efecto (apoyado por `match cut`, §9).
- **R14.6 (SHOULD)** **Pago de promesas**: lo introducido en el hook debe
  resolverse visualmente en el cierre.
- **R14.7 (MUST)** Cada escena debe tener una **idea visual dominante**; los
  planos la sirven, no la dispersan.

---

## 15. Quality Bar (criterio de aceptación)

Un documental cumple esta spec cuando, de forma verificable:

1. Ninguna escena es un solo plano sostenido (R1.1, R13.5).
2. Todos los planos tienen movimiento motivado (R2.1) salvo `static` deliberado.
3. Hay variedad de `shot_type`, `CameraMove`, óptica, luz, duración y `asset_type`
   (R13.*).
4. Cada `prompt` cumple la gramática completa (R12.1).
5. El ritmo y la luz siguen la emoción de la escena (R6.1, R7.1).
6. Las transiciones son corte directo por defecto, con efectos solo motivados
   (R9.1).
7. Existe un arco visual con hook, escalada, clímax y cierre (R8.6, R7.2, R14.6).

---

## 16. Estado y vinculación

- **Estado:** especificación normativa, independiente de implementación.
- **Vinculación:** el VIS (ARCH-VIS) DEBE seguir esta spec; cada decisión de un
  `Shot` debe poder justificarse citando una regla (`Rx.y`). Las tablas de
  mapeo (shot_type→cámara→duración, emoción→luz/óptica/ritmo) son la base de las
  implementaciones deterministas `Rule*`; las implementaciones LLM recibirán esta
  spec como sistema de instrucciones.
- **Cambios:** este documento es la fuente de verdad del lenguaje visual; cualquier
  evolución del look del canal se hace **aquí primero**, y el VIS se ajusta.
```
