# EAE — Evidence Acquisition Engine (foundation, EAE-001)

Motor permanente para **localizar, adquirir, organizar y verificar EVIDENCIAS reales** de
un caso documental. Este sprint construye **solo la arquitectura** (modelos, interfaces y
contratos): no descarga contenido, no hace peticiones, no scraping, no IA/LLM. Escribe solo
en `output/eae/` (nunca en `knowledge/`).

## Qué es una evidencia

Una unidad con **origen rastreable**: fotografía, vídeo, documento, noticia, mapa, rueda de
prensa, entrevista, PDF, archivo judicial, publicación oficial, cronología, comunicado,
audio o publicación pública en redes. Toda evidencia lleva su `EvidenceSource` (proveedor +
URL/ID + editor) — la raíz de la **cadena de custodia**.

## Qué NO es una evidencia

- Una imagen **generada** por IA (eso es un asset del ALR, no una evidencia).
- Un dato **sin origen** rastreable.
- Una **interpretación** o conclusión (eso es narrativa, no adquisición).

## Cadena de custodia, verificación y duplicados

- **Cadena de custodia** (`ChainOfCustody`): pasos auditables origen → adquisición →
  almacenamiento → uso. Cada evidencia la arranca al adquirirse.
- **Verificación** (`EvidenceVerifier`): comprobará fuente y hashes y asignará
  `VERIFIED/UNVERIFIED/DISPUTED/FAILED` + confianza. En EAE-001 devuelve `UNVERIFIED`/
  `UNKNOWN` (contrato; nunca inventa).
- **Duplicados** (`EvidenceDeduplicator`): estrategias hash perceptual / hash exacto / hash
  de metadatos / identidad de fuente. Contrato (devuelve `UNKNOWN`); no calcula todavía.

## Proveedores (contratos; sin red en EAE-001)

`youtube`, `wikimedia`, `internet_archive`, `news`, `government`, `wayback`, `future`. Todos
implementan `EvidenceProvider` (`search`→[] , `fetch`→NotImplementedError). Añadir una
fuente nueva = una clase más, sin tocar el orquestador.

## Estructura de la biblioteca (objetivo)

```
output/eae/cases/<case_id>/
  people/ locations/ timeline/ photos/ videos/ documents/ maps/ articles/ social/ metadata/
```

## Investigation Planner (EAE-002) — planificar antes de descargar

Antes de adquirir nada, el EAE construye un **plan de investigación**: responde "¿qué
material necesito realmente para producir este documental?". `EvidenceInvestigationPlanner`
recibe **solo** un `CaseProfile` y produce, de forma **determinista** (sin red, sin IA), un
`InvestigationPlan` con:

- **EvidenceNeed**: por cada necesidad, su `EvidenceCategory` (PHOTO, SCENE_PHOTO,
  COURT_DOCUMENT, NEWS, MAP, INTERVIEW, ARCHIVE_VIDEO, TIMELINE…), `EvidencePriority`
  (CRITICAL/HIGH/MEDIUM/LOW/OPTIONAL) y una `CoverageRequirement` (mínimo, ideal, conseguido,
  faltantes, % cobertura, estado).
- **SearchTask** + **AcquisitionTask** por necesidad. La adquisición apunta al **mínimo**
  necesario, no al ideal → **minimiza descargas** (nunca "descargar 200 fotos").
- **EvidenceManifest**: descripción completa del proyecto (personas, lugares, cronología,
  material esperado, cobertura deseada, fuentes prioritarias, restricciones, licencias,
  estado de cobertura, material pendiente/conseguido). Sin binarios.
- **ResearchStage**: Discovery → Verification → Acquisition → Organization.

**Cómo se calcula la cobertura:** cada necesidad declara un mínimo y un ideal; `acquired`
es 0 en planificación (nunca se inventa), así que todo arranca `PENDING` y el `%` se calcula
`acquired/minimum`. La cobertura solo sube cuando se adquiera material real (sprints futuros).

Pipeline: `Case → Investigation Planner → Evidence Manifest → Discovery → Verification →
Acquisition → Workspace`. Persistencia: `output/eae/plans/<case_id>/plan.json` (reproducible).

## Workspace temporal: material efímero, conocimiento permanente

Todo el material adquirido vivirá **solo** dentro del *workspace* del proyecto y se
**eliminará automáticamente** al terminar el documental. Permanecen únicamente: metadatos,
referencias, hashes, licencias, cadena de custodia y conocimiento. Nunca se conservan fotos
ni vídeos descargados salvo decisión explícita del usuario. (Igual que la política del DLE:
el binario es un medio; el conocimiento es la fuente de verdad.)

## Objetivo del motor

Construir una **biblioteca documental verificada** del caso ANTES de narrar o generar nada.
Separación total de responsabilidades (ver ADR-0016):

```
Adquisición (EAE) → Verificación (EAE) → Organización (EAE) → Narrativa → Generación
```

Nunca se mezclan. El EAE no genera documentales ni decide la narrativa: solo reúne y
verifica las evidencias y las pone a disposición de las fases siguientes.

## Módulos

`models.py` (Evidence/Source/Case/Person/Location/Event/Timeline/…), `interfaces.py`
(Protocols: Provider/Verifier/Collector/Storage/Deduplicator/Ranker/Resolver/Searcher +
`EvidenceQuery`), `providers/` (7 contratos), `verification.py`, `deduplication.py`,
`storage.py`, `orchestrator.py` (coordina), `persistence.py` (output/eae/).

Ver `docs/adr/ADR-0016-Evidence-Acquisition-Engine.md`.
