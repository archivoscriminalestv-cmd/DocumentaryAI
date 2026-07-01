# Architectural Backlog — DocumentaryAI

> Documento vivo, mantenido **con** el Documentary Chief Architect (DCA). Es la **memoria
> estratégica permanente** del proyecto y la fuente oficial para responder:
> **"¿Qué sabemos hoy que debemos mejorar en DocumentaryAI?"**
>
> No es un `TODO.md`. Es un documento arquitectónico de alto nivel.
>
> **Reglas:** el backlog se edita **a mano**. El DCA solo **propone** cambios (carga el
> documento, lo valida y emite un `BacklogProposal`); el desarrollador los aprueba e integra
> aquí. Ningún sprint comienza sin que el DCA revise antes este backlog. Los elementos resueltos
> **nunca se borran**: se mueven a *Completed*.
>
> **Estados permitidos** (toda entrada): `IDEA → PLANNED → DESIGNED → IN_PROGRESS → COMPLETED`,
> o `REJECTED`. Convención por entrada: encabezado `####` + metadatos `- **clave:** valor`.

---

## 1. Vision

DocumentaryAI aspira a producir **documentales completos, veraces y con calidad de cadena**
(Netflix/HBO/BBC/NatGeo) de forma **autónoma y reproducible**, usando prioritariamente recursos
**gratuitos y verificables**. El sistema aprende continuamente de documentales reales, investiga
y verifica evidencias de un caso, decide **cómo** contar la historia, genera imagen/voz/vídeo y
**evalúa su propia distancia respecto al corpus aprendido** para mejorar sprint a sprint.

Principios permanentes: **conocimiento por encima del binario** (el material es un medio; el
conocimiento es la verdad), **UNKNOWN antes que inventar**, **evidencia real antes que
recreación**, arquitectura **aditiva y desacoplada** (motores pequeños tras contratos), y
**trazabilidad total** de cada decisión. La meta operativa es cerrar la brecha medida por la
auditoría de capacidad (readiness operativa ~37 %, alineación con corpus 20 %) hasta un
documental de calidad ≥ 90 %.

---

## 2. Strategic Priorities

### P0 — Imprescindibles antes de producción

#### Channel Intelligence Engine (CIE)
- **id:** `cie`
- **status:** PLANNED
- **related:** `feedback_youtube`

Debe aprender automáticamente de YouTube: retención, CTR, engagement, comentarios, SEO,
monetización, duración y capítulos. Convierte el rendimiento real del canal en conocimiento
accionable para la generación. Complementa al YIE (que analiza un vídeo antes de aprender) con
inteligencia a nivel de **canal**.

#### Documentary Duration Planner
- **id:** `documentary_duration_planner`
- **status:** IDEA

Debe decidir la **duración óptima**, cuándo **dividir** un documental, sus **capítulos** y su
**ritmo**. Nunca alargar artificialmente un vídeo: la duración la dicta la materia y la retención,
no un objetivo arbitrario. Encaja como contrato aguas arriba del NAR (pacing) y del Composer.

#### Monetization & Compliance Engine
- **id:** `monetization_compliance_engine`
- **status:** IDEA

Debe validar automáticamente, **antes de publicar**: copyright, contenido reutilizado,
*advertiser-friendly*, *community guidelines*, riesgo de *strikes* y monetización. Es una puerta
de calidad/legal previa a la publicación, no un motor de generación.

#### Evidence Discovery Expansion
- **id:** `evidence_discovery_expansion`
- **status:** PLANNED
- **related:** `workspace_asset_policy`

El Discovery actual localiza sobre todo **fotografías**. Debe evolucionar para buscar también:
noticias, hemerotecas, vídeos, mapas, documentos judiciales y policiales, libros, entrevistas,
ruedas de prensa, archivos históricos, audio, televisión, podcasts y publicaciones oficiales.
No solo imágenes. (La auditoría confirmó Commons devolviendo 0 fotos y dimensiones documentales
en MISSING.)

#### Workspace Asset Policy
- **id:** `workspace_asset_policy`
- **status:** PLANNED
- **related:** `evidence_discovery_expansion`

Todo el material **gratuito** será temporal (se elimina al terminar el documental). Todo el
material adquirido mediante **APIs de pago** debe poder **conservarse y reutilizarse** en futuros
documentales. Debe existir una política explícita de reutilización de activos (se apoya en la
filosofía de workspace temporal del EAE y en el ALR para activos generados).

### P1 — Muy importantes

#### Integración completa VUE → VIS/VAI
- **id:** `vue_vis_vai_integration`
- **status:** PLANNED

El VUE produce conocimiento visual (composición, color, layout) que la generación aún **no
consume** (`knowledge_unused`, `not_integrated` en el DCA). Integrarlo en VIS/VAI por composición.

#### Music Knowledge
- **id:** `music_knowledge`
- **status:** IDEA

Sintetizar conocimiento musical del corpus (intensidad, energía, evolución, cambios). Hoy el KBG
reporta música 0/4 (todo UNKNOWN). Alimentaría un futuro MusicEngine.

#### Narrative Learning
- **id:** `narrative_learning`
- **status:** IDEA

Aprender **estructuras narrativas reales** del corpus (no solo métricas de plano/edición).
Alimentaría al NAR con distribuciones de estructura/beat reales en vez de reglas fijas. Hoy el
KBG reporta `structure`/`narrative_type` = UNKNOWN.

#### Advisor Evolution
- **id:** `advisor_evolution`
- **status:** IDEA

El Advisor debe pasar de **detectar** problemas a **proponer** soluciones accionables (manteniendo
su naturaleza objetiva, sin puntuación subjetiva).

#### Feedback desde YouTube
- **id:** `feedback_youtube`
- **status:** IDEA
- **related:** `cie`

Cuando el canal exista, aprender de Analytics: retención, CTR, comentarios, tiempo visto y
abandono. Cierra el lazo producción → publicación → aprendizaje.

### P2 — Mejoras futuras

#### Narración y localización multi-idioma
- **id:** `multilang_narration`
- **status:** IDEA

Producir el mismo documental en varios idiomas (narración y textos en pantalla) reutilizando el
mismo blueprint narrativo y los mismos activos.

### P3 — Ideas de investigación

#### Generación auto-mejorable en lazo cerrado
- **id:** `closed_loop_self_improvement`
- **status:** IDEA
- **related:** `feedback_youtube`

Investigar un lazo cerrado en el que las métricas reales del canal ajusten automáticamente las
decisiones de generación (estructura, ritmo, miniatura), siempre con aprobación humana.

---

## 3. Open Ideas

Ideas registradas **sin diseñar todavía**. No se convierten en RFC automáticamente: solo quedan
anotadas para no perderse entre conversaciones.

#### Pipeline de recreaciones (cuando falta evidencia real)
- **id:** `recreation_rendering_pipeline`
- **status:** IDEA
- **related:** `evidence_discovery_expansion`

El NAR ya marca *dónde* una recreación está justificada (evidencia real ausente + candidato del
ECE). Falta el motor que **produzca** esas recreaciones de forma explícita y trazable, sin
confundirlas con evidencia real.

#### Thumbnail & Title Intelligence
- **id:** `thumbnail_title_intelligence`
- **status:** IDEA
- **related:** `cie`

Decidir miniatura y título a partir del conocimiento del canal (CTR) y del blueprint narrativo
(gancho/hook), de forma objetiva y auditable.

---

## 4. Hypotheses

Hipótesis pendientes de validar. Cada una con `hypothesis: UNKNOWN | VALIDATED | REJECTED`.

#### Consumir el corpus en VAI/VIS sube la alineación
- **id:** `h_corpus_consumption_alignment`
- **status:** IDEA
- **hypothesis:** UNKNOWN

Si VAI consume color/movimiento y VIS consume duración/ritmo del corpus, el `corpus_alignment`
medido por el DCA superará el 0,20 actual. (Las divergencias hoy son del 72–100 %.)

#### La estructura de misterio mejora la retención en true_crime
- **id:** `h_mystery_structure_retention`
- **status:** IDEA
- **hypothesis:** UNKNOWN

Si el NAR usa `MYSTERY_INVESTIGATION` para true_crime, la retención real (cuando exista canal)
será mayor que con una estructura lineal. Validable solo con Feedback desde YouTube.

---

## 5. Technical Debt

Deuda arquitectónica conocida (hechos, no opiniones).

#### VAI no consume luz/movimiento del corpus
- **id:** `debt_vai_corpus_unused`
- **status:** PLANNED
- **related:** `vue_vis_vai_integration`

El corpus indica color cálido y movimiento sutil; la generación produce neutro/dinámico
(divergencia 100 %). El DCA marca VAI como siguiente motor a mejorar.

#### VIS no consume duración/ritmo del corpus
- **id:** `debt_vis_pacing_unused`
- **status:** PLANNED

Duración media de plano 5,12 s generada vs 2,97 s del corpus (72 %); pacing `slow` vs `moderate`.

#### Conocimiento aprendido no consumido por la generación
- **id:** `debt_knowledge_unused`
- **status:** IDEA
- **related:** `vue_vis_vai_integration`

El DCA detecta `knowledge_unused` en DLE, DKS, Advisor y YIE, y VUE `not_integrated`. Conocimiento
que se aprende pero no llega a la generación.

---

## 6. Completed

Elementos ya resueltos. **Nunca se eliminan**: se mueven aquí desde su sección original con su
estado final `COMPLETED` (o `REJECTED`).

_(Sin entradas todavía. Las propuestas aprobadas por el desarrollador se moverán aquí.)_
