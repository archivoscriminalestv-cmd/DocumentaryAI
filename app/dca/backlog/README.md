# DCA Backlog — Architectural Backlog (DCA-004)

La **memoria estratégica permanente** de DocumentaryAI. Una capacidad **nueva** del Documentary
Chief Architect (no un motor aparte, no un `TODO.md`): registra mejoras, ideas, hipótesis y
deuda arquitectónica para responder a la pregunta oficial del proyecto:

> **"¿Qué sabemos hoy que debemos mejorar en DocumentaryAI?"**

## Dos piezas

1. **Documento humano** — `docs/roadmap/ARCHITECTURAL-BACKLOG.md`. Alto nivel, editado **a
   mano**. Es la fuente de verdad.
2. **Soporte del DCA** — `app/dca/backlog/`. Carga el documento en modelos, lo valida y
   **propone** cambios tras cada sprint. **Nunca** reescribe el documento.

## Secciones del documento (exactas)

1. **Vision** — qué pretende llegar a ser DocumentaryAI.
2. **Strategic Priorities** — clasificadas `P0` (imprescindible antes de producción), `P1` (muy
   importante), `P2` (mejora futura), `P3` (investigación).
3. **Open Ideas** — ideas sin diseñar (no se convierten en RFC automáticamente).
4. **Hypotheses** — cada una con `hypothesis: UNKNOWN | VALIDATED | REJECTED`.
5. **Technical Debt** — deuda arquitectónica conocida.
6. **Completed** — resueltos; **nunca se eliminan**, se mueven aquí.

## Estados permitidos (toda entrada)

`IDEA → PLANNED → DESIGNED → IN_PROGRESS → COMPLETED` · `REJECTED`

## Convención parseable

Cada entrada es un encabezado `####` con metadatos en líneas `- **clave:** valor`:

```
#### Channel Intelligence Engine (CIE)
- **id:** `cie`
- **status:** PLANNED
- **related:** `yie`, `feedback_youtube`

Descripción libre / viñetas…
```

La prioridad se hereda del subencabezado `### P0 …`; en *Hypotheses* se añade
`- **hypothesis:** UNKNOWN`.

## Módulos

- `models.py` — `BacklogEntry`, `ArchitecturalBacklog`, `BacklogProposal`, enums de estado.
- `loader.py` — parsea el `.md` → modelos (determinista).
- `validator.py` — coherencia: estados/prioridades/hipótesis válidos, ids únicos, `related`
  resuelven, *Completed* solo COMPLETED/REJECTED.
- `updater.py` — dado el resumen de un sprint, **propone** resueltos, cambios de estado (valida
  transiciones), ideas nuevas y relaciones. No escribe el documento.
- `orchestrator.py` — `BacklogOrchestrator`: `load / validate / review / summary`.
- `persistence.py` — escribe propuestas/snapshots en `output/dca/backlog/`. Rechaza
  `knowledge/` y `docs/roadmap/`.

## Uso desde el DCA (por composición)

```python
dca = DocumentaryChiefArchitect()
backlog = dca.backlog()                 # carga el documento en modelos
issues  = dca.validate_backlog()        # coherencia
proposal = dca.review_backlog({         # propuesta tras un sprint (no escribe el .md)
    "sprint": "NAR-001",
    "resolved": ["narrative_director_missing"],
    "new_ideas": [{"title": "Narrative Learning from corpus", "section": "OPEN_IDEAS"}],
})
```

## Regla obligatoria del proyecto

A partir de DCA-004, **ningún sprint empieza** sin que el DCA revise primero el backlog:
¿resuelve algún punto?, ¿hay que actualizar estados?, ¿crea dependencias?, ¿aparecen ideas
nuevas? Y al terminar, el DCA emite un `BacklogProposal` que el desarrollador aprueba e integra
a mano en el documento.

Ver `docs/adr/ADR-0027-Architectural-Backlog.md`.
