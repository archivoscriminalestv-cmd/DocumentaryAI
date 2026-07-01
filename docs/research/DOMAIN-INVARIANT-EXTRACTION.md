# DOMAIN INVARIANT EXTRACTION — DocumentaryAI (WP-0021)

| Campo | Valor |
|---|---|
| **Document ID** | RES-DOMAIN-INVARIANT-EXTRACTION |
| **Title** | Domain Invariant Extraction — DocumentaryAI |
| **Status** | Draft (extraction) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | ARCH-0002; WP-0007…WP-0020 (ver §4) |

> **Documento de extracción, exclusivamente recopilatorio.** Extrae y organiza las invariantes presentes en ARCH-0002 y WP-0007…WP-0020.
> **No** crea invariantes nuevas, **no** reformula su significado, **no** resuelve conflictos, **no** prioriza y **no** diseña el dominio. Cada invariante incluye su **evidencia textual** verbatim.

---

## 1. Método y leyenda

- **Explícitas:** enunciados normativos directos (principalmente ARCH-0002: principios AP, §5, §6, §8, §9, §10).
- **Implícitas:** principios recurrentes con carácter de invariante presentes en WP-0007…WP-0020 (que eran documentos descriptivos; aquí solo se **extraen**, no se elevan a norma).
- **Tipo:** Epistemológica · Operativa · Trazabilidad · Aprendizaje · Calidad.
- **Absoluta / Contextual:** **solo observación** sobre cómo está redactada (p. ej. "never optional" vs "only when"); **no** es una decisión.
- "Capacidades relacionadas" referencia identificadores de **WP-0013**.

> Nota: pueden existir invariantes que se **solapan o repiten** entre fuentes (p. ej. trazabilidad aparece en AP-004, §9 y §10). Se listan por separado según su origen; **no** se fusionan ni se resuelven conflictos (restricción del WP).

---

## 2. Invariantes explícitas (ARCH-0002)

### INV-001 — Knowledge First
- **Descripción:** el conocimiento es el producto primario; el contenido es derivado.
- **Origen:** ARCH-0002 §7 AP-001.
- **Evidencia textual:** "Knowledge is the primary product. Content is a derived artifact."
- **Conceptos:** Knowledge, Content/Artifact.
- **Tipo:** Epistemológica.
- **Capacidades:** CAP-10, CAP-29 (y, como derivado, producción CAP-13…CAP-20).
- **Absoluta/Contextual:** parece absoluta (principio).

### INV-002 — Research Centric
- **Descripción:** todo trabajo significativo pertenece a un proceso de investigación.
- **Origen:** ARCH-0002 §7 AP-002.
- **Evidencia textual:** "All meaningful work belongs to a research process. Research is the fundamental business activity of the platform."
- **Conceptos:** Research, Work.
- **Tipo:** Operativa.
- **Capacidades:** CAP-33 (contenedor), CAP-01…CAP-29.
- **Absoluta/Contextual:** parece absoluta.

### INV-003 — Evidence Before Knowledge
- **Descripción:** no hay conocimiento sin evidencia; la evidencia precede a la interpretación.
- **Origen:** ARCH-0002 §7 AP-003.
- **Evidencia textual:** "Knowledge cannot exist without supporting evidence. Evidence precedes interpretation."
- **Conceptos:** Evidence, Knowledge, Interpretation.
- **Tipo:** Epistemológica.
- **Capacidades:** CAP-06, CAP-08, CAP-10, CAP-31.
- **Absoluta/Contextual:** parece absoluta.

### INV-004 — Traceability by Design
- **Descripción:** todo artefacto de conocimiento debe preservar su procedencia; la trazabilidad es obligatoria.
- **Origen:** ARCH-0002 §7 AP-004.
- **Evidencia textual:** "Every knowledge artifact must preserve its provenance. Traceability is a mandatory domain property. It is never optional."
- **Conceptos:** Knowledge artifact, Provenance, Traceability.
- **Tipo:** Trazabilidad.
- **Capacidades:** CAP-30, CAP-06, CAP-13.
- **Absoluta/Contextual:** absoluta ("never optional").

### INV-005 — Assertion traceable to evidence
- **Descripción:** toda afirmación debe poder rastrearse hasta la evidencia que la respalda.
- **Origen:** ARCH-0002 §5.
- **Evidencia textual:** "Every assertion should ultimately be traceable back to supporting evidence."
- **Conceptos:** Assertion, Evidence, Traceability.
- **Tipo:** Trazabilidad.
- **Capacidades:** CAP-31, CAP-08, CAP-13, CAP-30.
- **Absoluta/Contextual:** intención absoluta, redactada con "should ultimately".

### INV-006 — Knowledge explainable
- **Descripción:** el conocimiento debe permanecer explicable.
- **Origen:** ARCH-0002 §5.
- **Evidencia textual:** "Knowledge must remain explainable."
- **Conceptos:** Knowledge.
- **Tipo:** Calidad (y Trazabilidad).
- **Capacidades:** CAP-10.
- **Absoluta/Contextual:** parece absoluta.

### INV-007 — Stages preserve traceability
- **Descripción:** cada etapa añade interpretación preservando la trazabilidad a las etapas previas.
- **Origen:** ARCH-0002 §5.
- **Evidencia textual:** "Each stage adds interpretation while preserving traceability to previous stages."
- **Conceptos:** Source, Evidence, Knowledge, Narrative, Learning, Interpretation, Traceability.
- **Tipo:** Trazabilidad.
- **Capacidades:** ciclo CAP-06…CAP-29.
- **Absoluta/Contextual:** parece absoluta.

### INV-008 — Knowledge is not documents
- **Descripción:** el conocimiento no equivale a los documentos.
- **Origen:** ARCH-0002 §5.
- **Evidencia textual:** "Within DocumentaryAI, knowledge is not equivalent to documents."
- **Conceptos:** Knowledge, Document.
- **Tipo:** Epistemológica.
- **Capacidades:** CAP-06/CAP-07 (documentos) vs CAP-10 (conocimiento).
- **Absoluta/Contextual:** parece absoluta.

### INV-009 — AI never defines the domain
- **Descripción:** la IA asiste pero nunca define el dominio; los conceptos valen con cualquier proveedor/modelo.
- **Origen:** ARCH-0002 §7 AP-005.
- **Evidencia textual:** "Artificial Intelligence never defines the domain. All domain concepts must remain valid regardless of the AI provider or model employed."
- **Conceptos:** AI, Domain.
- **Tipo:** Operativa.
- **Capacidades:** todas (transversal).
- **Absoluta/Contextual:** absoluta ("never").

### INV-010 — Capability Independence
- **Descripción:** las capacidades perduran; las implementaciones evolucionan.
- **Origen:** ARCH-0002 §7 AP-006.
- **Evidencia textual:** "Capabilities endure. Implementations evolve."
- **Conceptos:** Capability, Implementation.
- **Tipo:** Operativa.
- **Capacidades:** las 33 capacidades.
- **Absoluta/Contextual:** parece absoluta.

### INV-011 — Automation only if it increases knowledge
- **Descripción:** la automatización vale solo si incrementa el conocimiento reutilizable.
- **Origen:** ARCH-0002 §7 AP-007.
- **Evidencia textual:** "Automation is valuable only when it increases reusable knowledge."
- **Conceptos:** Automation, Knowledge.
- **Tipo:** Aprendizaje.
- **Capacidades:** capacidades automatizables (cf. WP-0012 §7).
- **Absoluta/Contextual:** condicional ("only when") → se lee contextual.

### INV-012 — Evolution through validated learning
- **Descripción:** la plataforma evoluciona por aprendizaje validado; el MVP valida hipótesis de dominio.
- **Origen:** ARCH-0002 §7 AP-008.
- **Evidencia textual:** "The platform evolves through validated learning. The MVP exists to validate domain hypotheses rather than to maximize automation or feature count."
- **Conceptos:** Learning, MVP, Hypothesis.
- **Tipo:** Aprendizaje.
- **Capacidades:** CAP-29.
- **Absoluta/Contextual:** parece absoluta (principio).

### INV-013 — Every completed project must improve the platform
- **Descripción:** cada proyecto completado debe mejorar la plataforma.
- **Origen:** ARCH-0002 §6.
- **Evidencia textual:** "Every completed research project must improve the platform."
- **Conceptos:** Research project, Learning.
- **Tipo:** Aprendizaje.
- **Capacidades:** CAP-29, CAP-26, CAP-27.
- **Absoluta/Contextual:** absoluta ("must").

### INV-014 — Platform identity constraints (is NOT)
- **Descripción:** la plataforma no es ninguno de un conjunto de sistemas enumerados.
- **Origen:** ARCH-0002 §8.
- **Evidencia textual:** "DocumentaryAI is **not**: a document management system; a knowledge graph; a multi-agent platform; a video editor; a video generation platform; a workflow automation engine."
- **Conceptos:** identidad de la plataforma.
- **Tipo:** Operativa / Calidad.
- **Capacidades:** transversal (restricción de identidad).
- **Absoluta/Contextual:** absoluta (restricción).

### INV-015 — Traceability never sacrificed for convenience
- **Descripción:** la trazabilidad no se sacrifica por conveniencia.
- **Origen:** ARCH-0002 §10.
- **Evidencia textual:** "traceability shall never be sacrificed for convenience".
- **Conceptos:** Traceability.
- **Tipo:** Trazabilidad.
- **Capacidades:** CAP-30.
- **Absoluta/Contextual:** absoluta ("never").

### INV-016 — Reusable knowledge preferred over transient outputs
- **Descripción:** se prefiere el conocimiento reutilizable a las salidas transitorias.
- **Origen:** ARCH-0002 §10.
- **Evidencia textual:** "reusable knowledge shall be preferred over transient outputs".
- **Conceptos:** Knowledge (reusable), Output.
- **Tipo:** Aprendizaje / Calidad.
- **Capacidades:** CAP-10, CAP-29.
- **Absoluta/Contextual:** regla de preferencia → se lee contextual.

### INV-017 — Research remains the central business activity
- **Descripción:** la investigación permanece como la actividad central.
- **Origen:** ARCH-0002 §10.
- **Evidencia textual:** "research shall remain the central business activity".
- **Conceptos:** Research.
- **Tipo:** Operativa.
- **Capacidades:** CAP-33, CAP-01…CAP-29.
- **Absoluta/Contextual:** absoluta (reitera AP-002).

### INV-018 — Learning as a first-class concern
- **Descripción:** el aprendizaje se trata como preocupación de primer nivel.
- **Origen:** ARCH-0002 §10.
- **Evidencia textual:** "learning shall be treated as a first-class architectural concern."
- **Conceptos:** Learning.
- **Tipo:** Aprendizaje.
- **Capacidades:** CAP-29.
- **Absoluta/Contextual:** parece absoluta.

### INV-019 — Domain concepts independent of AI technologies
- **Descripción:** los conceptos del dominio permanecen independientes de las tecnologías de IA.
- **Origen:** ARCH-0002 §10.
- **Evidencia textual:** "domain concepts shall remain independent of AI technologies".
- **Conceptos:** Domain, AI.
- **Tipo:** Operativa.
- **Capacidades:** transversal.
- **Absoluta/Contextual:** absoluta (reitera AP-005).

### INV-020 — Evidence traceable throughout the process
- **Descripción:** la evidencia permanece trazable a lo largo de todo el proceso (criterio de éxito).
- **Origen:** ARCH-0002 §9.
- **Evidencia textual:** "evidence remains traceable throughout the process".
- **Conceptos:** Evidence, Traceability.
- **Tipo:** Trazabilidad.
- **Capacidades:** CAP-30, ciclo CAP-06…CAP-29.
- **Absoluta/Contextual:** parece absoluta (como criterio de éxito).

---

## 3. Invariantes implícitas (WP-0007…WP-0020)

> Principios recurrentes con carácter de invariante extraídos de documentos **descriptivos**; se citan como aparecen, sin elevarlos a norma.

### INV-021 — Evidence is a relational role
- **Descripción:** algo es evidencia en relación con una hipótesis; no es una clase de objeto fija.
- **Origen:** WP-0007, WP-0011, WP-0019.
- **Evidencia textual:** "la **naturaleza relacional de la evidencia**" / "algo es evidencia **respecto a** una hipótesis" (WP-0011 §5).
- **Conceptos:** Evidence, Hypothesis.
- **Tipo:** Epistemológica.
- **Capacidades:** CAP-31, CAP-08.
- **Absoluta/Contextual:** observación recurrente.

### INV-022 — Separation fact ↔ interpretation
- **Descripción:** se separa lo constatado (inmutable) de su interpretación (mutable).
- **Origen:** WP-0007, WP-0010, WP-0011, WP-0019.
- **Evidencia textual:** "**Separación hecho ↔ interpretación** (constatación inmutable vs valoración mutable)" (WP-0011 §5.1).
- **Conceptos:** Fact, Interpretation.
- **Tipo:** Epistemológica.
- **Capacidades:** CAP-08, CAP-09.
- **Absoluta/Contextual:** observación recurrente.

### INV-023 — Knowledge is provisional / revisable
- **Descripción:** el conocimiento es provisional y revisable (no monotonía).
- **Origen:** WP-0010, WP-0011.
- **Evidencia textual:** "**Conocimiento provisional y revisable** (inmutabilidad del registro + revisión/refutación)" (WP-0011 §5.1).
- **Conceptos:** Knowledge.
- **Tipo:** Epistemológica / Calidad.
- **Capacidades:** CAP-10.
- **Absoluta/Contextual:** observación recurrente.

### INV-024 — Provenance is transversal
- **Descripción:** la procedencia es transversal y crítica en todo el proceso.
- **Origen:** WP-0011, WP-0016.
- **Evidencia textual:** "**Procedencia como concepto transversal y crítico**" (WP-0011 §5.1).
- **Conceptos:** Provenance.
- **Tipo:** Trazabilidad.
- **Capacidades:** CAP-30.
- **Absoluta/Contextual:** observación recurrente (concuerda con INV-004).

### INV-025 — Uncertainty is explicit and graded
- **Descripción:** la incertidumbre se representa de forma explícita y graduada.
- **Origen:** WP-0010, WP-0011.
- **Evidencia textual:** "**Incertidumbre explícita y graduada**" (WP-0011 §4 / §5).
- **Conceptos:** Confidence, Uncertainty.
- **Tipo:** Calidad / Epistemológica.
- **Capacidades:** CAP-32.
- **Absoluta/Contextual:** observación recurrente.

### INV-026 — Capability functional prerequisites
- **Descripción:** una capacidad requiere que sus prerrequisitos funcionales estén disponibles (p. ej. no se publica sin exportación, empaquetado, metadatos y derechos).
- **Origen:** WP-0013, WP-0014.
- **Evidencia textual:** "CAP-24 Publicación | CAP-20, CAP-21, CAP-22, CAP-23" (WP-0014 §4 — dependencias).
- **Conceptos:** Capability, Dependency.
- **Tipo:** Operativa.
- **Capacidades:** CAP-24 (y, en general, cada capacidad respecto a sus dependencias).
- **Absoluta/Contextual:** contextual (depende de cada cadena de dependencias).

---

## 4. Observaciones (descriptivas)

- **Concentración por tipo:** la **Trazabilidad** aparece reiterada (INV-004, INV-005, INV-007, INV-015, INV-020, INV-024); el **Aprendizaje** también (INV-011, INV-012, INV-013, INV-016, INV-018); ambas reflejan el peso de AP-004 y de la "Continuous Learning" en ARCH-0002.
- **Solapamientos** (no resueltos): INV-004 ↔ INV-015 ↔ INV-020 ↔ INV-024 (trazabilidad/procedencia); INV-002 ↔ INV-017 (research centric); INV-005 ↔ INV-007 (afirmación/etapas trazables). Se listan por separado por origen distinto.
- **Posible tensión** (no resuelta): INV-002/INV-017 (Research Centric) y la dualidad de núcleo Research/Knowledge Base de **WP-0020** conviven con INV-001 (Knowledge First); se constata sin priorizar.
- **Redacción:** la mayoría se redacta en términos absolutos ("must", "never", "shall"); algunas son condicionales/preferencia (INV-011, INV-016) o dependientes de contexto (INV-026).
- Todo se ha **extraído**, no reformulado ni decidido.

---

## 5. Referencias cruzadas

- ARCH-0002 · `docs/architecture/ARCH-0002-Domain-Philosophy.md`
- WP-0007 · `docs/architecture/Evidence-Centric-Domain-Research.md`
- WP-0010 · `docs/research/EPISTEMIC-DOMAIN-PATTERN-RESEARCH.md`
- WP-0011 · `docs/research/DOMAIN-EVIDENCE-SYNTHESIS-MATRIX.md`
- WP-0013 · `docs/research/MVP-CAPABILITY-INVENTORY.md`
- WP-0014 · `docs/research/CAPABILITY-DEPENDENCY-MAP.md`
- WP-0016 · `docs/research/KNOWLEDGE-ASSET-INVENTORY.md`
- WP-0019 · `docs/research/DISCOVERY-TO-DOMAIN-MAPPING.md`
- WP-0020 · `docs/research/AGGREGATE-CANDIDATE-ANALYSIS.md`

---

_Fin de la extracción. Documento exclusivamente recopilatorio: no crea invariantes nuevas, no reformula su significado, no resuelve conflictos, no prioriza y no diseña el dominio. Insumo para RFC-0002 — Domain Model._
