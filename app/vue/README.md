# VUE — Visual Understanding Engine (foundation, VUE-001)

El VUE comprende el **contenido visual** de cada plano. VUE-001 fijó la arquitectura;
**VUE-002** añade los primeros detectores REALES de **visión clásica** (solo Pillow +
matemáticas; sin IA/Deep Learning/OpenCV/numpy). Sigue **completamente independiente**: no
se integra (todavía) con DLE/DKS/Production Advisor/VAI/Composer.

> Nota: OpenCV/numpy no están instalados (y el guard del paquete los prohíbe). La visión
> clásica se implementa con Pillow (filtro de bordes + umbral en lugar de Canny,
> histogramas, geometría, diferencia de fotogramas). Determinista y reproducible.

## Detectores reales (VUE-002) — solo hechos objetivos

| Detector | `value` | `facts` que mide | NO mide |
|----------|---------|------------------|---------|
| `CompositionDetector` | UNKNOWN* | centro de masa (x,y), equilibrio izq/dcha y sup/inf, offset a los tercios, espacio negativo | intención artística / "buena composición" |
| `ColorAnalysisDetector` | color dominante | paleta, temperatura, saturación, contraste, brillo, exposición (clipping), histograma RGB | estética / estado de ánimo |
| `EdgeDensityDetector` | UNKNOWN* | densidad de bordes, % textura, complejidad, rejilla 3×3 de detalle, celda más densa | qué objeto hay |
| `MotionEnergyDetector` | UNKNOWN* | diff absoluta media, % píxeles cambiados, intensidad (2 frames) | tipo de movimiento de cámara |
| `FrameGeometryDetector` | orientación | resolución, aspect ratio, letterbox, pillarbox, márgenes negros | — |

\* `value` es la **clasificación categórica**; estos detectores miden hechos pero no
clasifican, así que `value=UNKNOWN` y la medida vive en `facts` (con `method="classical_cv"`).
`confidence` es siempre `None` (jamás se inventa una puntuación). Las capacidades aún no
implementadas (shot_size/face/text/evidence/scene_type/object/map/document) siguen como
esqueletos UNKNOWN (`method="not_implemented"`).

## Disposición y localización (VUE-003) — geometría objetiva del plano

| Detector | `value` | `facts` que mide | NO mide |
|----------|---------|------------------|---------|
| `SubjectLocalizationDetector` | UNKNOWN* | bbox de la región saliente, centro, ocupación, distancias a cada borde, margen libre, posición relativa | qué es el sujeto (no reconoce objetos) |
| `LayoutBalanceDetector` | UNKNOWN* | distribución horizontal/vertical (tercios), simetría horiz/vert, concentración, dispersión | si la composición es "buena" |
| `VisualWeightDetector` | UNKNOWN* | peso visual izq/dcha/arriba/abajo, centro de gravedad | intención del encuadre |
| `EmptySpaceDetector` | UNKNOWN* | % de espacio vacío, mayor región vacía (bbox), distribución del espacio negativo | el porqué del espacio negativo |

El **sujeto** se localiza por **saliencia clásica** (bordes/contraste), no por reconocimiento
de objetos; si nada destaca → `UNKNOWN` (nunca inventa).

### Para qué sirve después

Estos hechos geométricos son la **base** sobre la que se construirán, en sprints
posteriores, los clasificadores cinematográficos **sin** volver a medir píxeles:
- **Shot Size Detector**: usará `subject_localization.occupancy` + márgenes (un sujeto que
  ocupa mucho ⇒ primer plano; poco ⇒ plano general).
- **Composition Detector**: usará `layout_balance` (simetría/tercios), `visual_weight`
  (centro de gravedad) y `empty_space` para clasificar la composición.

Primero la geometría objetiva; la interpretación cinematográfica vendrá encima.

## Qué hace

- Coordina **detectores** independientes (uno por capacidad visual) sobre un `FrameRef`
  (referencia de fotograma provider-agnóstica) y reúne sus `VisualObservation` en un
  `VisualAnalysis`.
- Devuelve **solo hechos observables**, versionados y serializables.

## Qué NO hace

- **No** infiere, opina, ni puntúa de forma inventada (`confidence = None` si no se mide).
- **No** usa IA generativa ni visión por computador en este sprint (sin OpenCV/YOLO/
  Florence/GroundingDINO/Gemini/GPT Vision).
- **No** mezcla detección con interpretación. **UNKNOWN antes que inventar.**
- **No** escribe en `knowledge/` (el writer apunta a `output/vue/`).
- **No** modifica ni depende de ningún otro subsistema.

## Módulos

| Módulo | Responsabilidad |
|--------|-----------------|
| `models.py` | `VisualObservation`, `VisualAnalysis`, vocabularios (`ShotSize`/`Composition`/`SceneType`/`EvidenceType`), payloads (`FaceLayout`/`DetectedText`/`ObjectDetection`) |
| `interfaces.py` | `FrameRef` + `VisualDetector` (Protocol) |
| `detectors.py` | Detectores esqueleto (una capacidad cada uno; devuelven UNKNOWN) |
| `orchestrator.py` | `VisualUnderstandingEngine` — solo coordina; nunca implementa lógica; no rompe ante fallos |
| `persistence.py` | Contrato serializable (`to_payload`/`from_payload`) + `VisualAnalysisWriter` (output/vue/) |

## Cómo añadir un detector nuevo

1. Implementa la interfaz `VisualDetector`: una clase con `capability: str` y
   `detect(frame, context=None) -> VisualObservation`.
2. Devuelve solo hechos objetivos; usa `UNKNOWN` y `confidence=None` cuando no haya medida.
3. Regístralo: `engine.register(MyDetector())`, o añádelo a `default_detectors()`.

El orquestador no cambia: solo conoce la interfaz. Sustituir el esqueleto por una
implementación real (OpenCV/YOLO/…) no afecta a modelos, contrato ni orquestador.

## Integración futura (no en este sprint)

- **DLE**: por cada fotograma representativo de un plano, el DLE podrá invocar el VUE y
  guardar las `VisualObservation` (p.ej. `shot_size`, `composition`) en
  `knowledge/documentaries/<id>/`, eliminando los `UNKNOWN` actuales del análisis.
- **DKS / Production Advisor**: agregarán esos hechos (cobertura real de capacidades).
- **VAI / Composer**: podrán usar el entendimiento del corpus para decidir/ejecutar.

Ver `docs/adr/ADR-0015-Visual-Understanding-Engine.md`.
