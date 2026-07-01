# DocumentaryAI Chief Architect (DCA) — `app/dca/`

El **arquitecto permanente** de DocumentaryAI: el "gemelo digital" del sistema. Comprende
toda la arquitectura (motores, dominios, capacidades, dependencias, pipeline, documentación)
y la expone como un modelo consultable y auditable.

> NO es un motor de generación. No analiza vídeos, no aprende, no descarga, no llama a IA,
> no genera imágenes, no ejecuta el pipeline y **no modifica ningún subsistema**. Solo
> lectura, determinista, mediante contratos públicos. `UNKNOWN` antes que inventar. Escribe
> solo en `output/dca/`. Ver `docs/adr/ADR-0020`.

## Componentes
- **registry.py** — registro PÚBLICO y manual de los motores (nombre, dominio,
  responsabilidad, entradas/salidas/artefactos, dependencias, capacidades, estado, docs).
  No autodescubre nada.
- **capability_graph.py** — quién produce / consume cada capacidad.
- **dependency_graph.py** — dependencias directas e indirectas, ciclos, aislados, hojas.
- **architecture_reader.py** — lee solo documentación pública (ADR/RFC/SPEC/README). Nunca
  código privado ni introspección.
- **analyzer.py** — qué motores hay, qué falta (capacidades sin productor), qué está
  duplicado, qué no usa nadie, qué conocimiento no aprovecha la generación.
- **roadmap.py** — roadmap determinista por reglas objetivas (tipo de hueco, nº de
  consumidores afectados, estado). Sin IA, sin scoring subjetivo.
- **orchestrator.py** — `DocumentaryChiefArchitect`: `snapshot()/analyze()/recommend()/
  roadmap()/architecture()/capabilities()/dependencies()`. Solo coordinación.
- **persistence.py** — escribe el modelo en `output/dca/`.

## CLI
```
python -m app.cli.architecture_report
# -> output/dca/{architecture,capability_graph,dependency_graph,roadmap,recommendations}.json
#    + architecture_report.md
```

## Objetivo
A partir de este sprint, cualquier decisión de desarrollo futura debería poder responderse
consultando al DCA en lugar de depender de recordar conversaciones antiguas. Es la base para
que DocumentaryAI planifique su propia evolución de forma objetiva y auditable. La
inteligencia avanzada (impacto, simulación de mejoras) llegará en sprints posteriores; esta
primera versión construye el modelo arquitectónico completo.

## Self Evaluation (DCA-003) — `app/dca/evaluation/`

El DCA gana una capacidad NUEVA (no un motor aparte): cerrar el ciclo
`Generación → Aprendizaje`. Mide OBJETIVAMENTE la distancia entre el documental generado y el
conocimiento del corpus y propone el siguiente motor a mejorar. Sin IA, sin opinión, solo
lectura de contratos públicos (ProductionContext/VisualPlan/Evidence Coverage/Recreation
Candidates), determinista, `UNKNOWN` antes que inventar.

- **comparator.py** — mide por dimensión (ritmo, duración media de plano, movimiento, color,
  iluminación, cobertura de evidencias, uso de recreaciones, cronología): corpus vs generado +
  desviación + estado.
- **gap_analyzer.py** — convierte las diferencias en huecos (HECHOS, nunca opiniones) y mapea
  cada uno a su **motor responsable** (shot_duration→VIS, movement/color→VAI, lighting→VUE,
  coverage→EAE, chronology→ECE, …).
- **roadmap_generator.py** — prioriza por reglas objetivas: nº de consumidores afectados (grafo
  de capacidades del DCA) + magnitud del hueco + huecos arquitectónicos (motores no integrados).
- **System Health** — indicadores derivados de datos: knowledge_utilization, generation_coverage,
  corpus_alignment, evidence_coverage, unknown_decisions, integrated/missing capabilities.

API: `DocumentaryChiefArchitect.evaluate(production_context=…, visual_plans=[…], ece_coverage=…,
recreation_candidates=…, generation_knowledge=…)`. CLI: `python -m app.cli.self_evaluation`.
Salidas en `output/dca/`: `evaluation.json`, `generation_vs_corpus.json`, `improvement_plan.json`,
`system_health.json`, `evaluation_report.md`. Ver `docs/adr/ADR-0023`.

Así DocumentaryAI ya no depende solo del desarrollador para decidir qué construir: mide su
distancia al corpus y propone el siguiente paso arquitectónico de forma auditable.
