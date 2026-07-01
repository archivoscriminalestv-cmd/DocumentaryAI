# Architecture Index

# Introducción

Este documento es el **punto de entrada** a la documentación de arquitectura de DocumentaryAI.
Su finalidad es que cualquier desarrollador o asistente de IA pueda, de un vistazo:

- saber **qué carpetas** componen `docs/architecture`,
- saber **qué documentos existen**, de qué **tipo** son y en qué **estado**,
- y disponer de un **orden de lectura recomendado** según su rol.

Es un índice descriptivo: no resume el contenido de los documentos ni introduce arquitectura.
Refleja el estado real de `docs/architecture` en la fecha de su creación (2026-06-27).
Actualizado el **2026-06-28** para reflejar el cierre de **WP-0009** (ver «Evidencia arquitectónica del proyecto», «Registro de conclusiones arquitectónicas», «Estado del Sprint A-01» y «Próximo hito»).
Actualizado el **2026-06-28** por **DS-0003**: cierre formal de Discovery, registro de ARCH-0002, DS-0001 y DS-0002, registro de WP-0010…WP-0022 como evidencia arquitectónica, y nueva sección «Normative Documents Pending».
Actualizado el **2026-06-28**: registro de **ADR-0001 — Research is the Operational Unit** como documento normativo **Approved** (ver «Normative Documents (Approved)»).
Actualizado el **2026-06-28**: registro de **ADR-0002 — Knowledge Accumulation is the Core Value** como documento normativo **Approved**.
Actualizado el **2026-06-28** por **DS-0010**: registro de **WP-0024** y **WP-0025** como evidencia de Discovery, cierre definitivo de Discovery y nota de base normativa para RFC-0002.

---

# Estructura documental

Carpetas existentes bajo `docs/architecture`:

```
docs/architecture/
├── ADR/         (carpeta — contiene solo .gitkeep)
├── diagrams/    (carpeta — contiene solo .gitkeep)
└── templates/   (carpeta — plantillas de documentación)
```

Notas:
- `ADR/` y `diagrams/` están vacías salvo por un archivo `.gitkeep` que preserva la carpeta en Git.
- `templates/` contiene las plantillas reutilizables de documentación.

---

# Documentos

> "Estado" se indica solo cuando puede deducirse del propio documento.
> Documentos vacíos (0 bytes) se marcan como **Reserved**.
> Las descripciones se toman del propósito declarado por cada documento; no se inventan.

### Nivel `docs/architecture/`

| Documento | Tipo | Estado | Descripción (de una línea) |
|---|---|---|---|
| `Architecture-Index.md` | Index | No declarado | Punto de entrada a la documentación de arquitectura (este documento). |
| `Architecture-Audit.md` | Review / Audit | No declarado en el documento | Auditoría solo de observación de la documentación del proyecto. |
| `Document-Header-Standard.md` | Standard | No declarado en el documento | Estándar de cabecera documental (front matter en Markdown) para los documentos oficiales. |
| `RFC-0001-Architecture.md` | RFC | Reserved (vacío) | Reserved |
| `glossary.md` | Glossary | Reserved (vacío) | Reserved |
| `ARCH-0002-Domain-Philosophy.md` | ARCH | Approved | Principios filosóficos del dominio; normativo para la arquitectura (registrado por DS-0003). |
| `REPOSITORY-STRUCTURE-AUDIT.md` | Review / Audit | Draft (audit) | Auditoría de divergencias estructurales del repositorio (DS-0002). |

### Nivel `docs/architecture/templates/`

| Documento | Tipo | Estado | Descripción (de una línea) |
|---|---|---|---|
| `templates/RFC-template.md` | Template | N/A (plantilla) | Plantilla para proponer un cambio o idea y abrirlo a discusión antes de adoptarlo. |
| `templates/ADR-template.md` | Template | N/A (plantilla) | Plantilla para registrar una decisión de arquitectura ya tomada, su contexto y sus consecuencias. |
| `templates/ARCH-template.md` | Template | N/A (plantilla) | Plantilla para describir la arquitectura de un sistema o subsistema: componentes, relaciones y vistas. |
| `templates/SPEC-template.md` | Template | N/A (plantilla) | Plantilla para definir con precisión qué debe construirse: requisitos, interfaces y criterios de aceptación. |
| `templates/Review-template.md` | Template | N/A (plantilla) | Plantilla para registrar el resultado de una revisión: hallazgos por severidad y recomendaciones. |

### Carpetas de marcadores

| Ruta | Tipo | Estado | Descripción (de una línea) |
|---|---|---|---|
| `ADR/.gitkeep` | Placeholder | Reserved (vacío) | Reserved |
| `diagrams/.gitkeep` | Placeholder | Reserved (vacío) | Reserved |

---

# Navegación recomendada

> Órdenes de lectura sobre los documentos **existentes**. Los marcados como *Reserved* se incluyen
> al final porque aún no tienen contenido; se listan para que se conozcan y se vigile su redacción.

### Nuevo desarrollador
1. `Architecture-Index.md` (este índice).
2. `Document-Header-Standard.md` — cómo se estructuran las cabeceras de los documentos oficiales.
3. `templates/` — los tipos de documento del proyecto (RFC, ADR, ARCH, SPEC, Review).
4. `Architecture-Audit.md` — estado observado de la documentación.
5. *Reserved:* `RFC-0001-Architecture.md`, `glossary.md` (pendientes de contenido).

### Arquitecto
1. `Architecture-Index.md`.
2. `Architecture-Audit.md` — hallazgos y observaciones sobre la documentación.
3. `Document-Header-Standard.md` — estándar de cabecera a consolidar.
4. `templates/` — plantillas disponibles para redactar documentación oficial.
5. *Reserved (a redactar):* `RFC-0001-Architecture.md`, `glossary.md`.

### Implementation engineer
1. `Architecture-Index.md`.
2. `templates/SPEC-template.md` y `templates/Review-template.md` — formato de especificaciones y revisiones que guiarán la implementación.
3. `Document-Header-Standard.md` — cabecera a aplicar en los documentos.
4. *Reserved:* `RFC-0001-Architecture.md`, `glossary.md` (sin contenido implementable todavía).

---

# Evidencia arquitectónica del proyecto

> Documentos que, aun residiendo fuera de `docs/architecture/`, el Principal Architect ha incorporado como **evidencia arquitectónica** del proyecto.

| Documento | Tipo | Estado | Descripción (de una línea) |
|---|---|---|---|
| `docs/research/DOMAIN-ONTOLOGY-RESEARCH.md` (WP-0009) | Research | Approved | Investigación de la ontología del dominio; evidencia para ARCH-0002 y RFC-0002. |
| `docs/research/EPISTEMIC-DOMAIN-PATTERN-RESEARCH.md` (WP-0010) | Research | Registered (DS-0003) | Patrones epistémicos de 9 disciplinas. |
| `docs/research/DOMAIN-EVIDENCE-SYNTHESIS-MATRIX.md` (WP-0011) | Research | Registered (DS-0003) | Síntesis de WP-0007/0009/0010 por tema y consenso. |
| `docs/research/YOUTUBE-DOCUMENTARY-PRODUCTION-CAPABILITY-MAP.md` (WP-0012) | Research | Registered (DS-0003) | Mapa de capacidades de producción para YouTube. |
| `docs/research/MVP-CAPABILITY-INVENTORY.md` (WP-0013) | Research | Registered (DS-0003) | Inventario y clasificación funcional de capacidades del MVP. |
| `docs/research/CAPABILITY-DEPENDENCY-MAP.md` (WP-0014) | Research | Registered (DS-0003) | Dependencias funcionales entre capacidades. |
| `docs/research/DISCOVERY-INDEX.md` (WP-0015) | Research | Registered (DS-0003) | Índice de consolidación de Discovery. |
| `docs/research/KNOWLEDGE-ASSET-INVENTORY.md` (WP-0016) | Research | Registered (DS-0003) | Inventario de tipos de activos de conocimiento. |
| `docs/research/MVP-CAPABILITY-TRACEABILITY-MATRIX.md` (WP-0017) | Research | Registered (DS-0003) | Trazabilidad capacidades ↔ activos. |
| `docs/research/RESEARCH-LIFECYCLE-EXTRACTION.md` (WP-0018) | Research | Registered (DS-0003) | Ciclo de vida implícito de la investigación. |
| `docs/research/DISCOVERY-TO-DOMAIN-MAPPING.md` (WP-0019) | Research | Registered (DS-0003) | Puente conceptos Discovery → dominio. |
| `docs/research/AGGREGATE-CANDIDATE-ANALYSIS.md` (WP-0020) | Research | Registered (DS-0003) | Comparativa Research vs Knowledge Base. |
| `docs/research/DOMAIN-INVARIANT-EXTRACTION.md` (WP-0021) | Research | Registered (DS-0003) | Extracción de invariantes explícitas e implícitas. |
| `docs/research/CAPABILITY-COMMAND-MAPPING.md` (WP-0022) | Research | Registered (DS-0003) | Mapeo capacidad → acción observable. |
| `docs/research/UBIQUITOUS-LANGUAGE-EXTRACTION.md` (WP-0024) | Research | Registered (DS-0010) | Extracción y auditoría terminológica. |
| `docs/research/DOMAIN-OBJECT-INVENTORY.md` (WP-0025) | Research | Approved · Registered (DS-0010) | Inventario de objetos candidatos del dominio; entrada para RFC-0002. |

Estado de Work Packages reflejado:
- **WP-0009 — Domain Ontology Research:** Completado · **Status:** Approved · **Architectural Review:** Approved by Principal Architect · **Decision Date:** 2026-06-28.
- **WP-0010 … WP-0022:** Registrados como evidencia arquitectónica por **DS-0003** (2026-06-28).
- **ARCH-0002 — Domain Philosophy:** **Approved** (2026-06-28) · `docs/architecture/ARCH-0002-Domain-Philosophy.md`.
- **DS-0001 — Repository Foundation:** Implementado (estructura de directorios, plantillas en `templates/`, `CONTRIBUTING.md`, `docs/README.md`).
- **DS-0002 — Repository Standards Consolidation:** Auditoría · `docs/architecture/REPOSITORY-STRUCTURE-AUDIT.md`.
- **WP-0024 y WP-0025:** Registrados como evidencia de Discovery por **DS-0010** (2026-06-28); **WP-0025 — Domain Object Inventory: Approved**.

---

# Registro de conclusiones arquitectónicas

> Conclusiones decididas por el **Principal Architect** a partir de WP-0009. Se registran de forma literal; no son decisiones introducidas por el Developer.

- **AC-0001 — Terminología:** No existe una terminología universalmente aceptada para conceptos como Evidence, Observation, Fact, Claim, Finding o Conclusion. Su significado depende del contexto disciplinar.
- **AC-0002 — Estándares:** Ningún estándar externo (PROV, Dublin Core, CIDOC CRM, ISO 15489, OAIS, RDF u otros) se adopta como modelo conceptual del dominio. Todos quedan como referencias de investigación.
- **AC-0003 — Ubiquitous Language:** DocumentaryAI desarrollará un lenguaje ubicuo propio. La terminología oficial la definirá el Principal Architect durante el Sprint A-01, usando la investigación como evidencia, sin adoptar literalmente ninguna ontología existente.

---

# Estado del Sprint A-01 — Domain Discovery

| Actividad | Estado |
|---|---|
| Investigación documental | Complete |
| Investigación terminológica | Complete |
| Descubrimiento filosófico del dominio | Next |

---

# Próximo hito

- **ARCH-0002 — Domain Philosophy** es el siguiente entregable del Sprint A-01, a cargo del Principal Architect. Aún **no** existe documento ni borrador; se deja constancia únicamente como próximo hito (no se ha creado ni debe crearse todavía).

---

# Estado oficial de la fase

- **Discovery: CLOSED** — cerrada formalmente por **DS-0003** (2026-06-28).
- **ARCH-0002 — Domain Philosophy:** **Approved** y entregado. Esta entrada **supersede** la nota de «Próximo hito» que aún lo daba como pendiente (mantenida arriba como historial).
- Domain Discovery (Sprint A-01) y la investigación de MVP Definition (Sprint A-02, WP-0012…WP-0022) quedan consolidadas como evidencia arquitectónica.
- **Discovery cerrada definitivamente por DS-0010 (2026-06-28).** **WP-0007 → WP-0025** constituyen la **evidencia completa de Discovery** (WP-0008 es gobernanza, no Discovery; no existe WP-0023).
- **Base normativa para RFC-0002:** **ARCH-0002**, **ADR-0001** y **ADR-0002**.

---

# Normative Documents (Approved)

> Documentos normativos aprobados e incorporados al repositorio.

| Documento | Tipo | Estado | Ruta |
|---|---|---|---|
| ARCH-0002 — Domain Philosophy | ARCH | Approved | `docs/architecture/ARCH-0002-Domain-Philosophy.md` |
| ADR-0001 — Research is the Operational Unit | ADR | Approved | `docs/adr/ADR-0001-Research-is-the-Operational-Unit.md` |
| ADR-0002 — Knowledge Accumulation is the Core Value | ADR | Approved | `docs/adr/ADR-0002-Knowledge-Accumulation-is-the-Core-Value.md` |

> Nota: el propio ADR-0001 declara internamente `Status: Accepted`; se registra aquí como **Approved** conforme a la instrucción de incorporación (términos equivalentes).

---

# Normative Documents Pending

> Documentos normativos aún no creados. Conforme a `CONTRIBUTING.md`, ningún documento derivado puede adelantarse a su fuente normativa.

| Documento | Estado |
|---|---|
| RFC-0002 — Domain Model | Pending |
| SPEC-0001 | Skeleton (pendiente de contenido) |

---

# Observaciones

> Solo identificación de pendientes. No se proponen cambios.

- **Documentos Reserved (vacíos):** `RFC-0001-Architecture.md` y `glossary.md` están a 0 bytes, pendientes de redacción.
- **Carpetas vacías:** `ADR/` y `diagrams/` solo contienen `.gitkeep`; aún no albergan documentos ni diagramas.
- **Sin campo de estado:** `Architecture-Audit.md` y `Document-Header-Standard.md` no incluyen un campo de estado explícito, por lo que su estado no se ha podido declarar con certeza.
- **Tipo "Glossary" fuera del catálogo enumerado:** `glossary.md` no encaja en los tipos RFC/ADR/ARCH/SPEC/Standard/Template/Handbook; se ha clasificado como "Glossary".
- **Cobertura del índice:** la sección «Documentos» abarca `docs/architecture`. Además, la sección «Evidencia arquitectónica del proyecto» referencia, por decisión del Principal Architect, documentación situada fuera de esa carpeta (p. ej. `docs/research/`). Existe asimismo documentación de gobierno en `docs/` y `docs/governance/` que queda fuera del alcance de este índice.
- **Registro consolidado en el índice:** a falta de un fichero de registro de Work Packages/decisiones, el cierre de WP-0009, las conclusiones AC y el estado del Sprint se han reflejado en este índice para no crear nuevos tipos documentales. Si el Principal Architect prefiere registros dedicados, pueden separarse previa autorización.
