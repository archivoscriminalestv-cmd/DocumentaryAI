# Knowledge Bridge (KBG) — `app/kbg/`

El **KBG es la frontera entre Learning y Generation**. Convierte el conocimiento aprendido
por DocumentaryAI (estilos del DKS, corpus, YouTube, advisor, ECE…) en **decisiones
objetivas de generación** (`GenerationKnowledge`). Cierra el gap `knowledge_unused` detectado
por el DCA.

> No crea contenido, no analiza vídeos, no aprende, no ejecuta IA, no genera prompts ni
> imágenes y no decide estética subjetiva. Solo **traduce conocimiento en parámetros**, por
> composición y solo lectura. Determinista, provider-agnóstico. `UNKNOWN` antes que inventar.
> Escribe solo en `output/kbg/`. Ver `docs/adr/ADR-0021`.

```
Learning (DLE → DKS / YIE / VUE / EAE → ECE)
        │  conocimiento público (knowledge/styles, output/ece, …)
        ▼
      KBG  →  GenerationKnowledge.json   ← decisiones objetivas y trazables
        │
        ▼
Generation (VIS → VAI → Composer)   ← lo consumirán en sprints posteriores
```

## Componentes
- **models.py** — `Decision` (key, value, origin, confidence, knowledge_sources, reason) y
  `GenerationKnowledge` (decisiones por sección + summary).
- **knowledge_loader.py** — carga artefactos PÚBLICOS (knowledge/styles/, output/ece…). Nunca
  estado interno; si falta un fichero → `None` (UNKNOWN).
- **style_resolver.py** — resuelve por género: perfil del género + patrones del DKS
  (cinematography/editing/lighting/motion/documentary_style), fusión determinista con
  precedencia y fallback.
- **decision_engine.py** — reglas deterministas: distribución dominante (si `UNKNOWN` domina →
  decisión `UNKNOWN`), resúmenes numéricos, mezcla de evidencias desde el ECE.
- **bridge.py** — `KnowledgeBridge.build(genre, ece_coverage_path)` → `GenerationKnowledge`.
- **persistence.py** — escribe `output/kbg/GenerationKnowledge.json` + report.

## Decisiones (secciones)
storytelling · cinematography · editing · narration · music · evidence. Cada decisión lleva
**origen, confianza (derivada solo del dato), fuentes y motivo**. Ejemplo real (corpus de 98
documentales): `pacing = moderate (49%)`, `average_shot_duration = 2.97s`,
`color_temperature = warm (45%)`, `lighting = balanced (57%)`; `dominant_shot_size = UNKNOWN`
(el corpus aún no clasifica shot size).

## Uso
```
python -m app.cli.generation_knowledge --genre true_crime [--ece-coverage <coverage_report.json>]
```
Integración futura: VIS/VAI/Composer consumirán `GenerationKnowledge`; este sprint solo lo deja
preparado (no modifica la generación).
