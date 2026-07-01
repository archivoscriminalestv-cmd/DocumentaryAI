# Evidence Correlation Engine (ECE) — `app/ece/`

Hace que DocumentaryAI razone como un investigador documental: correlaciona las evidencias
(del EAE Discovery) en un **EvidenceGraph** tipado, analiza la **cobertura** por dimensiones,
registra **conflictos** sin decidir y detecta **candidatos de recreación** sin generarlos.

> Solo análisis. NO genera imágenes/vídeos, NO llama a modelos, NO infiere relaciones sin
> evidencia. Determinista. No toca DLE/YIE/VUE/VIS/VAI/Composer. Entrada: `InvestigationPlan`
> + `DiscoveryPlan` (EAE). Ver `docs/adr/ADR-0019`.

## Salida (en `output/projects/<case>/`)
- **evidence_graph.json** — nodos (Person/Event/Location/Evidence/Timeline/Organization) y
  relaciones tipadas (SAME_EVENT/SAME_LOCATION/SAME_PERSON/REFERENCES/SUPPORTS/CONTRADICTS/
  MENTIONS/DERIVED_FROM), cada una con las evidencias que la soportan.
- **coverage_report.json** — dimensiones (cronología, personas, lugares, fotografías, vídeos,
  documentos, audio, mapas, noticias) clasificadas COMPLETE / PARTIAL / MISSING.
- **conflicts.json** — datos contradictorios (p.ej. fechas) con todos los candidatos y
  `requires_verification = true` (nunca se decide).
- **recreation_candidates.json** — dónde PODRÍA hacer falta una recreación (segmento, motivo,
  cobertura existente, evidencias disponibles/ausentes, tipo sugerido, hechos en los que
  basarse). Nunca cuando ya hay evidencia real suficiente.

## Principio fundamental
La evidencia real tiene **prioridad absoluta**. La IA solo podrá complementar lo que no exista
documentalmente; las recreaciones nunca sustituyen ni se mezclan con las evidencias originales.
Todo queda trazado (ids de evidencia) y auditado.

## Uso
Integrado en `python -m app.cli.case_discovery` (tras el Discovery). Programático:
```python
from app.ece.engine import CaseCorrelationEngine
result = CaseCorrelationEngine().analyze(investigation_plan, discovery_plan)
```
