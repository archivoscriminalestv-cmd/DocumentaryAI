# Visual Intelligence System (VIS) — `app/vis/`

VIS-1 (`build_visual_plan`): `CinematicProfile` (RDA) + `Scene` → `VisualPlan` (planos con
tipo, cámara, iluminación, duración, grade). VIS-2 (`compile_execution`): `VisualPlan` →
`ExecutionPlan` (requests al MGL). Determinista, sin LLM, sin red.

## ProductionContext (frontera Knowledge → Generation)
Desde PCX-001, `build_visual_plan(..., context=ProductionContext)` puede recibir un
`ProductionContext` (PCX). **VIS solo conoce ese contrato**: nunca lee KBG ni `knowledge/`,
ni conoce DLE/DKS/YIE/EAE/ECE.

Cuando el contexto trae decisiones **conocidas** (no `UNKNOWN`) y con confianza suficiente,
estas tienen prioridad sobre las heurísticas del RDA:

| Decisión del contexto (sección.clave) | Efecto en VIS |
|---|---|
| `storytelling.average_shot_duration` | duración media de plano → nº de planos |
| `storytelling.pacing` | `pacing_tier` del plan |
| `cinematography.dominant_movement` | tendencia/repertorio de cámara (mapeado) |
| `cinematography.lighting` | iluminación de los planos |
| `cinematography.color_temperature` | temperatura del color grade |

Reglas (filosofía): las decisiones del contexto se aplican **solo cuando existen, no son
`UNKNOWN` y tienen confianza suficiente**. En cualquier otro caso —o si `context=None`— VIS
**genera exactamente el mismo storyboard que antes**. El contexto no sustituye las heurísticas:
solo las prioriza cuando hay conocimiento real. VIS queda desacoplado del origen del
conocimiento (todo llega vía `ProductionContext`).
