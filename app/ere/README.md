# Evidence Research Engine (ERE) — `app/ere/`

Subsistema **aditivo**, independiente y *superior* cuyo objetivo es localizar,
recopilar, normalizar y organizar la **evidencia pública** sobre un caso, y construir
un **EvidenceGraph** reproducible: la futura *fuente de verdad* del documental.

> El ERE **no** genera imágenes, prompts, personajes, vídeo ni consistencia. Solo
> investiga. **Nunca inventa**: si una fuente no existe, continúa. **Nunca rompe** el
> pipeline. No modifica CRE/VIS/VAI/VSC/VPL/Motion/Composer/FFmpeg.

## Arquitectura
```
ProjectQuery → EvidenceOrchestrator → [N EvidenceProviders] → GraphBuilder → EvidenceGraph
                                                                            ↘ evidence_manifest.json
                                                                            ↘ evidence_report.md
```
Posición en el sistema (futuro): `Project → ERE → EvidenceGraph → (Character/Location
Bibles, Timeline, Evidence Assets) → Character Consistency Engine → VSC → VPL → Motion
→ Composer`. El ERE solo construye el grafo; los consumidores se añadirán después.

## EvidenceGraph (modelo)
Grafo serializable, versionado y reproducible:
- **entities** (`Entity`): personajes/lugares/organizaciones — `id`, `type`,
  `canonical_name`, `aliases`, `attributes` (campo → lista de `Claim` con proveedor +
  confianza), `references` (ids de assets), `sources`, `metadata`.
- **events** (`Event`), **articles** (`Article`: headline/medium/date/url/snippet/
  entities_detected), **images** (`ImageAsset`), **videos** (`VideoAsset`),
  **court_documents** (`CourtDocument`: solo referencias públicas), **relationships**
  (`Relationship`: `source_id —relation→ target_id`) → es un **grafo**, no listas.
- **conflicts**, **providers_used**, **sources** (`SourceRef`: provider/url/source/
  confidence/license/hash/retrieved_at).
- Imágenes y vídeos solo se **catalogan** (sin descarga; `hash` reservado).

## Proveedores (plug-in: `EvidenceProvider`)
`real_providers(client, lang, seed)` (CLI por defecto):
- **Reales (sin clave):** `WikipediaProvider` (0.8), `WikidataProvider` (0.9),
  `CommonsProvider` (0.7).
- **Preparados** (interfaz lista, `available=False`, `client` inyectable): `News`,
  `Youtube`, `GoogleImages`, `Archive`, `CourtDocuments`. Son las fuentes clave para
  true-crime; requieren claves/acuerdos → se wirearán sin tocar el resto.
- **`SeedEvidenceProvider`**: normaliza evidencia pública **curada por el Director**
  (JSON) → la vía realista para casos sin presencia enciclopédica. No inventa ni
  interpreta; solo estructura lo aportado.
- **`MockEvidenceProvider`** (0.2): solo el nodo del sujeto desde el request.

`default_providers()` (offline/determinista: preparados + mock) → para tests.

La red está aislada tras `HttpClient` (`app/ere/http.py`) e **inyectable** → tests sin
red y deterministas.

## Confianza y conflictos
Cada `Claim`/`SourceRef` lleva `provider` + `confidence`. El `GraphBuilder` es
**determinista**: fusiona entidades por `id`, une alias/referencias, acumula todos los
claims y, **ante discrepancia, conserva todos los candidatos** en `conflicts` (no
decide). `canonical_name` toma el valor no vacío de mayor confianza.

## Artefactos
- `evidence_graph.json` — grafo reproducible (`sort_keys`, sin timestamp).
- `evidence_manifest.json` — proveedores, errores, estadísticas, cobertura, tiempos,
  `graph_checksum` (sha256) y `generated_at`.
- `evidence_report.md` — resumen, fuentes, cobertura, entidades, noticias, imágenes,
  vídeos, conflictos, licencias y nivel de confianza.

## CLI
```
python -m app.cli.research_evidence --project "Coquito"
python -m app.cli.research_evidence --project "Coquito" --location "Barcelona" --date "2021-01-04"
python -m app.cli.research_evidence --project "Coquito" --seed casos/coquito.seed.json
python -m app.cli.research_evidence --project "Coquito" --offline
# -> output/evidence/<slug>/{evidence_graph.json, evidence_manifest.json, evidence_report.md}
```

### Formato del seed (evidencia curada por el Director)
JSON con claves opcionales `entities`, `articles`, `images`, `videos`,
`court_documents`, `relationships` (ver docstring de `providers/seed.py`). Permite
construir un grafo rico de casos true-crime a partir de fuentes públicas reales sin
scraping.

## Decisiones arquitectónicas (ERE-001)
- **AD-1 — EvidenceGraph como fuente de verdad** versionada y reproducible (timestamp
  y checksum en el manifest, no en el grafo).
- **AD-2 — Plug-in `EvidenceProvider`**: el orquestador no conoce ninguna fuente; se
  añaden/wirean fuentes sin refactor.
- **AD-3 — Robustez total**: cada proveedor corre en `try/except`; una fuente que
  falla o no existe no rompe el pipeline (`available=False` + `error` al manifest).
- **AD-4 — Grafo, no listas**: relaciones tipadas entre nodos (`Relationship`).
- **AD-5 — Confianza + conflictos conservados**: nada sin procedencia; los desacuerdos
  no se deciden, se guardan.
- **AD-6 — Catálogo de evidencia sin descarga**: imágenes/vídeos solo metadatos
  (`hash` reservado); judicial solo referencias públicas, sin interpretación.
- **AD-7 — Independencia**: ERE no depende de CRE; un adaptador ERE→CharacterBible→CRE
  se construirá *después* (no ahora).

## ERE-002 — Query Builder + Ranking + Entity Resolution
Tres subsistemas independientes que actúan **antes** del grafo. Nuevo flujo:
```
ProjectKnowledge → QueryBuilder → Providers → RankingEngine → EntityResolver → EvidenceGraph
```
- **`ProjectKnowledge`** (`project_knowledge.py`): contexto documental (title,
  canonical_name, aliases, known_people, locations, dates, country, language, genre,
  keywords, documentary_type, notes). `to_query()` convierte el **sujeto real** en el
  nombre de búsqueda (p.ej. *Jonathan Burgos*) y deja el title (*Coquito*) como alias.
  CLI: `python -m app.cli.project_knowledge …` → `output/project/project_knowledge.json`.
- **Evidence Query Builder** (`query_builder.py`): estrategias plug-in
  (`Person/Alias/Location/Date/Keyword/Combined`) generan **múltiples** consultas
  enriquecidas; el Builder fusiona, deduplica y ordena por peso. Determinista.
- **Evidence Ranking Engine** (`ranking.py`): puntúa cada nodo con señales genéricas
  (nombre/alias/persona/ubicación/fecha/keywords = *contexto*; confianza/proveedor/
  idioma = *calidad*) y pesos configurables (`RankingWeights`). `score = contexto *
  (0.5 + 0.5·calidad)`. **Sin reglas por género**: el cóctel "Coquito" (solo coincide
  el alias) cae por debajo del umbral; el caso real (nombre+lugar+fecha+keyword) sube.
- **Entity Resolution Engine** (`entity_resolution.py`): agrupa entidades equivalentes
  (mismo nombre normalizado o alias del sujeto) en una sola, reapunta relaciones y
  recalcula conflictos. **No crea entidades nuevas**; solo agrupa las existentes.

Entrada ERE-002 (no cambia la estructura del grafo):
`EvidenceOrchestrator.research_project(knowledge, min_score=0.15)`; CLI:
`python -m app.cli.research_evidence --knowledge output/project/project_knowledge.json`.
El manifest añade `project_knowledge`, `query_builder` (consultas) y `ranking`
(aceptadas/descartadas con score).

### Decisiones arquitectónicas (ERE-002)
- **AD-8 — Nunca buscar solo un nombre:** se investiga un `ProjectKnowledge` (contexto),
  no una palabra.
- **AD-9 — Desambiguación por puntuación, no por reglas:** prohibido `if true_crime`;
  todo emerge de señales con pesos configurables → genérico y extensible.
- **AD-10 — Estrategias y señales plug-in:** añadir una `QueryStrategy` o una señal de
  ranking no toca el resto.
- **AD-11 — Resolución solo agrupa:** identidades equivalentes se unifican; no se
  inventan nodos. La relevancia la decide el Ranking; la identidad, la Resolution.

> Limitación de ERE-001 (falso positivo "Coquito" = cóctel) **resuelta**: con
> `ProjectKnowledge` el sujeto pasa a ser *Jonathan Burgos* y el ranking descarta los
> resultados sin contexto, de forma totalmente genérica.
