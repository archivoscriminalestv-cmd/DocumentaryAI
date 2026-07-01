# Production Advisor (`app/advisor/`) — ADV-001 scaffold + ADV-002 gap analyzer

Subsistema **completamente desacoplado** que analiza el conocimiento aprendido
(`knowledge/`) para responder preguntas estratégicas:

- ¿Qué le falta a DocumentaryAI para alcanzar la calidad del corpus?
- ¿Cuáles son las mayores diferencias entre nuestro pipeline y los documentales de éxito?
- ¿Qué capacidades aportarían mayor impacto?
- ¿Qué % del corpus usa imágenes reales, entrevistas, mapas, documentos, etc.?
- ¿Qué deberíamos desarrollar después?

**No genera documentales. No modifica ningún otro subsistema.** Solo **lee** artefactos
**públicos** de `knowledge/` (de forma defensiva, tolerante a escrituras concurrentes) y
escribe sus informes en `output/advisor/` (**nunca** en `knowledge/`).

**ADV-001** aportó la arquitectura (modelos/interfaces/lector/orquestador/persistencia).
**ADV-002** la convierte en un **comparador determinista corpus↔pipeline**: matriz de
cobertura de capacidades, gap analyzer real, ranking por **frecuencia observada**,
completitud del corpus, confianza por **tamaño muestral** y top discoveries. Sin IA, sin
pesos arbitrarios; lo no medido = `UNKNOWN`.

Salidas (`output/advisor/`): `production_advisor.md`, `capability_matrix.json`,
`gap_report.json`, `discoveries.json` (+ `advisor_report.{json,md}` de ADV-001).

Fuentes reales que mide el corpus (DKS `styles/*.json`): movement, lighting,
color_temperature, dominant_color, pacing, cuts/min. `shot_size`/`composition` salen
100% `UNKNOWN` (sin detector) → se reportan como *blind spots* de mayor frecuencia. Las
capacidades de producción (entrevistas/mapas/documentos/metraje real) no tienen señal
pública → `UNKNOWN` en el corpus y `MISSING` en el pipeline (hecho conocido), sin
cuantificar.

```
knowledge/ (público, solo lectura)
        │  KnowledgeReader (defensivo)
        ▼
CorpusSnapshot ── GapAnalyzer ──► gaps ── Recommender ──► recommendations
        └────────────────────────────────────────────────► AdvisorReport
                                                              │ ReportWriter
                                                              ▼
                                                output/advisor/advisor_report.{json,md}
```

## Módulos

| Módulo | Responsabilidad |
|--------|-----------------|
| `models.py` | `CorpusSnapshot`, `CapabilityUsage`, `GapFinding`, `Recommendation`, `AdvisorReport` + enums (`Dimension`/`Severity`/`Impact`/`Effort`) y taxonomía `CAPABILITIES` |
| `interfaces.py` | Protocolos públicos: `KnowledgeSource`, `GapAnalyzer`, `Recommender`, `ReportSink` |
| `knowledge_reader.py` | `KnowledgeReader` — lectura **solo-lectura** y defensiva de `knowledge/` → `CorpusSnapshot` |
| `analyzers.py` | `BaselineGapAnalyzer` + `BaselineRecommender` (esqueleto determinista) |
| `orchestrator.py` | `ProductionAdvisor.advise()` / `advise_and_write()` |
| `persistence.py` | `ReportWriter` → `output/advisor/` (nunca `knowledge/`) + `render_report` |

## Uso (programático)

```python
from app.advisor import ProductionAdvisor
report = ProductionAdvisor(knowledge_root="knowledge").advise()
# o, persistiendo en output/advisor/:
report, paths = ProductionAdvisor(knowledge_root="knowledge").advise_and_write()
```

## Decisiones / extensión futura

- Cobertura de capacidades en el corpus = **UNKNOWN** hasta que el corpus exponga señales
  públicas (entrevistas/mapas/documentos…). Nunca se inventa.
- `pipeline_supported` refleja hechos **conocidos** de nuestra generación (p.ej.
  narración/música sí; metraje real no).
- Los `GapAnalyzer`/`Recommender` son enchufables: la comparación real corpus↔pipeline y la
  priorización por impacto se implementarán en sprints posteriores sin tocar el orquestador.

Ver `docs/adr/ADR-0014-Production-Advisor.md`.
