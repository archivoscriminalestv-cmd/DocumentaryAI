# ADR-0027 — Architectural Backlog (Living Roadmap)

- **Status:** Accepted
- **Date:** 2026-07-01
- **Sprint:** DCA-004
- **Relates:** ADR-0020 (Chief Architect), ADR-0023 (Self-Evaluation), ADR-0026 (Narrative
  Intelligence Engine), y todos los ADR/RFC de motores

## Contexto

DocumentaryAI ya tiene decenas de motores, ADRs, RFCs y decisiones. Durante el desarrollo
aparecen continuamente ideas estratégicas, hipótesis y deuda arquitectónica que **se pierden
entre conversaciones**. Hace falta una **memoria estratégica permanente** —no un `TODO.md`—
que responda de forma oficial: *"¿Qué sabemos hoy que debemos mejorar en DocumentaryAI?"*

## Decisión 1 — Un documento humano de alto nivel

La fuente de verdad es `docs/roadmap/ARCHITECTURAL-BACKLOG.md`, editado **a mano**, con seis
secciones fijas: **Vision, Strategic Priorities (P0–P3), Open Ideas, Hypotheses, Technical
Debt, Completed**. Toda entrada vive en un único estado: `IDEA → PLANNED → DESIGNED →
IN_PROGRESS → COMPLETED`, o `REJECTED`. Los elementos resueltos **nunca se borran**: se mueven a
*Completed*. Las hipótesis llevan además `UNKNOWN | VALIDATED | REJECTED`.

## Decisión 2 — El DCA lo gestiona, por composición

Se añade `app/dca/backlog/` como **capacidad nueva del Documentary Chief Architect** (igual que
DCA-003 añadió la autoevaluación): `models / loader / validator / updater / orchestrator /
persistence`. El `DocumentaryChiefArchitect` expone `backlog()`, `validate_backlog()`,
`review_backlog()` y `backlog_summary()` delegando en `BacklogOrchestrator`. **No se modifica
`analyzer.py`** ni ningún otro motor, pipeline, generación o aprendizaje. Todo aditivo.

## Decisión 3 — El DCA propone; el humano aprueba

El backlog **nunca se reescribe automáticamente**. El DCA carga el documento en modelos, lo
valida y, tras un sprint, emite un `BacklogProposal` (resueltos, cambios de estado con
validación de transiciones, ideas nuevas, relaciones) que se persiste como artefacto en
`output/dca/backlog/`. El desarrollador lo aprueba e integra **a mano** en el documento. La
persistencia rechaza escribir en `docs/roadmap/` y en `knowledge/`.

## Decisión 4 — Regla obligatoria de proceso

A partir de DCA-004, **ningún sprint comienza** sin que el DCA revise antes el backlog: si el
sprint resuelve algún punto, si hay que actualizar estados, si crea dependencias y si aparecen
ideas nuevas. Al terminar, el DCA produce la propuesta de actualización.

## Decisión 5 — Las ideas no se convierten en RFC automáticamente

*Open Ideas* y las ideas nuevas detectadas solo **quedan registradas**. Promocionarlas a RFC o a
sprint es una decisión humana explícita. El backlog registra; no decide.

## Consecuencias

- **Positivo:** memoria estratégica permanente y auditable; el conocimiento estratégico deja de
  perderse entre conversaciones; el DCA cierra el lazo "sprint → actualización del roadmap" con
  trazabilidad; cero riesgo para el pipeline (solo lectura del documento + artefactos en
  `output/`); validación determinista del documento.
- **Limitaciones aceptadas:** el `updater` **no infiere** mágicamente qué resolvió un sprint —
  recibe el resumen del sprint y lo valida/normaliza (hay un `suggest_related` por keywords como
  ayuda, no como decisión); el parser exige la convención de metadatos `- **clave:** valor`; la
  edición del documento es manual por diseño.

## Entradas iniciales

Cargadas en el documento: **P0** — Channel Intelligence Engine (PLANNED), Documentary Duration
Planner (IDEA), Monetization & Compliance Engine (IDEA), Evidence Discovery Expansion (PLANNED),
Workspace Asset Policy (PLANNED). **P1** — Integración VUE→VIS/VAI (PLANNED), Music Knowledge
(IDEA), Narrative Learning (IDEA), Advisor Evolution (IDEA), Feedback desde YouTube (IDEA).
Además, deuda y hipótesis derivadas de la auditoría de capacidad real (VAI/VIS no consumen el
corpus; conocimiento aprendido no consumido).
