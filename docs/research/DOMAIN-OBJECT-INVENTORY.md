# DOMAIN OBJECT INVENTORY — DocumentaryAI (WP-0025)

| Campo | Valor |
|---|---|
| **Document ID** | RES-DOMAIN-OBJECT-INVENTORY |
| **Title** | Domain Object Inventory — DocumentaryAI |
| **Status** | Draft (inventory) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | ARCH-0002; ADR-0001; ADR-0002; WP-0007…WP-0024; DS-0004…DS-0007 |

> **Inventario, exclusivamente descriptivo.** Consolida los **objetos candidatos del dominio** como entrada para **RFC-0002 — Domain Model**.
> **No** decide el modelo, **no** define entidades/agregados/ownership/relaciones/estados, **no** propone comandos ni arquitectura y **no** interpreta el dominio. Cada objeto se traza a sus fuentes.

---

## 1. Método y leyenda

- **Fuentes (únicas):** ARCH-0002, ADR-0001, ADR-0002, WP-0007…WP-0024, DS-0004…DS-0007.
- **Campos por objeto:** Identificador · Nombre · Definición (derivada/citada) · Documentos · Papel observado · Activos relacionados · Capacidades relacionadas · Etapa del ciclo · Invariantes relacionadas · Observaciones.
- **Etapas (WP-0018/DS-0004):** E1 Investigación · E2 Narrativa · E3 Producción · E4 Publicación · E5 Aprendizaje · TR Transversal.
- **Agrupación:** por **familias observadas** (no se crean categorías nuevas). Un objeto puede tener varios roles; aquí solo se constata.
- La asignación a familia/etapa/papel es **descriptiva**, no normativa.

---

## 2. Inventario por familias

### Familia Research

- **OBJ-001 · Research** — *Def:* "unidad operacional"; "investigación delimitada en el tiempo y en el objetivo"; "transformar información externa en conocimiento reutilizable"; "no representa el conocimiento permanente" (ADR-0001 §2). *Docs:* ADR-0001, ADR-0002, WP-0018, WP-0020, DS-0004. *Papel:* unidad operacional / contenedor de trabajo. *Activos:* working set del proyecto. *Capacidades:* CAP-01…CAP-29, CAP-33. *Etapa:* todo el ciclo. *Invariantes:* INV-002, INV-017. *Obs:* **normativo (ADR-0001)**; subsume Case/Investigation.
- **OBJ-002 · Case** — *Def:* asunto investigado (contenedor) (WP-0009). *Docs:* WP-0009. *Papel:* contenedor (antecedente). *Capacidades:* CAP-33. *Etapa:* TR. *Invariantes:* —. *Obs:* solapa/subsumido por Research → **candidato a desaparecer / sinónimo**.
- **OBJ-003 · Investigation** — *Def:* proceso de indagación (WP-0009). *Docs:* WP-0009. *Papel:* proceso (antecedente). *Etapa:* TR. *Obs:* subsumido por Research → **duplicado/legacy**.
- **OBJ-004 · Workspace** — *Def:* "espacio organizativo. No describe un proceso" — **descartado** (ADR-0001 §6). *Docs:* ADR-0001. *Papel:* alternativa descartada. *Obs:* **candidato a desaparecer** (descartado normativamente).
- **OBJ-005 · Capability** — *Def:* algo que el proceso/sistema debe poder hacer (WP-0012/0013); "Capabilities endure" (ARCH-0002 AP-006). *Docs:* ARCH-0002, WP-0012/0013/0014. *Papel:* habilidad del dominio. *Etapa:* todas. *Invariantes:* INV-010. *Obs:* recurrente.
- **OBJ-006 · Objective** — *Def:* metas del proyecto (WP-0012 C-03). *Docs:* WP-0012/0013. *Capacidades:* CAP-03. *Etapa:* E1. *Obs:* artefacto no inventariado (WP-0017 §4).
- **OBJ-007 · Topic / Theme** — *Def:* tema seleccionado (WP-0012 C-02). *Docs:* WP-0012/0013. *Capacidades:* CAP-02. *Etapa:* E1.
- **OBJ-008 · Research Plan / Question** — *Def:* preguntas y plan de investigación (WP-0012 C-04). *Docs:* WP-0012/0013. *Activos:* Preguntas. *Capacidades:* CAP-04. *Etapa:* E1.

### Familia Knowledge

- **OBJ-010 · Knowledge** — *Def:* información estructurada, contextualizada y justificada (WP-0009; ARCH-0002 §5); producto primario (AP-001). *Docs:* ARCH-0002, WP-0009/0010/0011/0016, ADR-0002. *Papel:* producto primario. *Activos:* Conocimiento. *Capacidades:* CAP-10. *Etapa:* E1 (salida). *Invariantes:* INV-001, INV-006, INV-016, INV-023. *Obs:* recurrente.
- **OBJ-011 · Knowledge Base** — *Def:* "activo permanente de DocumentaryAI"; "toda Research existe para incrementar la Knowledge Base" (ADR-0002 §2). *Docs:* ADR-0002, WP-0020. *Papel:* patrimonio permanente. *Invariantes:* INV-013, INV-016, INV-018. *Obs:* **normativo (ADR-0002)**; distinto de Knowledge.
- **OBJ-012 · Hypothesis** — *Def:* explicación tentativa contrastable (WP-0009/0010). *Docs:* WP-0009/0010/0012/0013. *Capacidades:* CAP-10. *Etapa:* E1.
- **OBJ-013 · Conclusion** — *Def:* afirmación final del razonamiento (WP-0009). *Docs:* WP-0009/0010. *Capacidades:* CAP-10. *Etapa:* E1.
- **OBJ-014 · Finding** — *Def:* resultado de un análisis (WP-0009). *Docs:* WP-0009/0010/0012. *Capacidades:* CAP-09. *Etapa:* E1.
- **OBJ-015 · Information** — *Def:* nivel previo al conocimiento (DIKW) (WP-0011). *Docs:* WP-0011. *Obs:* **ambiguo** (frontera difusa con Knowledge).
- **OBJ-016 · Pattern** — *Def:* patrón epistémico/de investigación reutilizable (WP-0010/0016). *Docs:* WP-0010, WP-0016. *Papel:* activo reutilizable.
- **OBJ-017 · Lessons learned / Learning** — *Def:* aprendizaje reutilizable; "Every completed research project must improve the platform" (ARCH-0002 §6). *Docs:* ARCH-0002, WP-0012/0013, ADR-0002. *Capacidades:* CAP-29. *Etapa:* E5. *Invariantes:* INV-012, INV-013, INV-016, INV-018.

### Familia Evidence

- **OBJ-020 · Evidence** — *Def:* info/material que apoya o refuta una afirmación; "Evidence precedes interpretation" (ARCH-0002 AP-003; WP-0009/0011); rol relacional. *Docs:* ARCH-0002, WP-0007/0009/0010/0011, DS-0004. *Capacidades:* CAP-06, CAP-08, CAP-31. *Etapa:* E1/TR. *Invariantes:* INV-003, INV-004, INV-021. *Obs:* recurrente; material vs relación.
- **OBJ-021 · Evidence Item** — *Def:* unidad discreta de evidencia (WP-0009). *Docs:* WP-0009. *Obs:* **ambiguo** (granularidad); solapa con Evidence/Document.
- **OBJ-022 · Observation** — *Def:* constatación directa previa a interpretación (WP-0009). *Docs:* WP-0009, WP-0012. *Capacidades:* CAP-06. *Etapa:* E1.
- **OBJ-023 · Claim** — *Def:* enunciado propuesto como verdadero, sujeto a respaldo (WP-0009). *Docs:* WP-0009/0010/0011. *Capacidades:* CAP-06, CAP-08, CAP-13. *Invariantes:* INV-005. *Obs:* **nombre duplicado** con Assertion/Statement.
- **OBJ-024 · Assertion** — *Def:* acto/proposición afirmada (WP-0009). *Docs:* WP-0009. *Obs:* **duplicado** con Claim/Statement.
- **OBJ-025 · Statement** — *Def:* enunciado (WP-0010). *Docs:* WP-0010. *Obs:* **duplicado** con Claim/Assertion.
- **OBJ-026 · Fact** — *Def:* afirmación verificable tenida por cierta (WP-0009/0010). *Docs:* WP-0009/0010/0011. *Capacidades:* CAP-08. *Obs:* **ambiguo** (umbral de "hecho").
- **OBJ-027 · Source** — *Def:* origen del que procede info/material (WP-0009). *Docs:* WP-0009/0010, DS-0004. *Activos:* Lista de fuentes. *Capacidades:* CAP-05. *Etapa:* E1.
- **OBJ-028 · Document** — *Def:* unidad de contenido registrada; portador (WP-0009); "knowledge is not equivalent to documents" (ARCH-0002 §5). *Docs:* WP-0007/0009, WP-0012. *Capacidades:* CAP-06. *Obs:* **tensión**: ADR-0002 "el dominio no gestiona documentos" → **candidato a desaparecer/ambiguo**.
- **OBJ-029 · Confidence / Uncertainty** — *Def:* grado de certeza graduable / su falta (WP-0010/0013). *Docs:* WP-0010/0011/0013. *Capacidades:* CAP-32. *Invariantes:* INV-025. *Obs:* familia con Certainty.
- **OBJ-030 · Trust (reliability/credibility)** — *Def:* fiabilidad de fuente / credibilidad de info (WP-0011). *Docs:* WP-0010/0011. *Obs:* **ambiguo**; no nombrado en WP-0009.
- **OBJ-031 · Justification** — *Def:* respaldo que distingue conocimiento de creencia (WP-0010/0011). *Docs:* WP-0010/0011. *Obs:* solapa con Evidence/Provenance.
- **OBJ-032 · Interpretation** — *Def:* valoración mutable frente al hecho constatado (WP-0007/0010/0011). *Docs:* WP-0007/0010/0011, WP-0019. *Capacidades:* CAP-08, CAP-09. *Invariantes:* INV-022.

### Familia Provenance

- **OBJ-040 · Provenance** — *Def:* origen e historia de un material/afirmación (WP-0009); "Traceability… never optional" (ARCH-0002 AP-004). *Docs:* ARCH-0002, WP-0007/0009/0011, WP-0016. *Capacidades:* CAP-30. *Etapa:* TR. *Invariantes:* INV-004, INV-015, INV-020, INV-024. *Obs:* recurrente; consenso alto.
- **OBJ-041 · Metadata** — *Def:* datos que describen otros datos (WP-0009). *Docs:* WP-0009. *Capacidades:* CAP-05, CAP-07. *Obs:* solapa con Provenance/Annotation.
- **OBJ-042 · Citation** — *Def:* indicación formal de la fuente (WP-0009). *Docs:* WP-0009. *Obs:* **duplicado** con Reference.
- **OBJ-043 · Reference** — *Def:* apuntador a un recurso (WP-0009). *Docs:* WP-0009. *Obs:* **duplicado** con Citation.
- **OBJ-044 · Annotation** — *Def:* información añadida por un analista (WP-0009). *Docs:* WP-0009. *Obs:* dato vs interpretación.

### Familia Narrative

- **OBJ-050 · Narrative concept** — *Def:* ángulo/tono/arco (WP-0012 C-11). *Docs:* WP-0012. *Capacidades:* CAP-11. *Etapa:* E2. *Obs:* artefacto no inventariado.
- **OBJ-051 · Structure / Outline** — *Def:* escaleta/estructura (WP-0012 C-12). *Docs:* WP-0012. *Capacidades:* CAP-12. *Etapa:* E2. *Obs:* no inventariado.
- **OBJ-052 · Script (Guion)** — *Def:* texto narrado del documental (WP-0012/0013). *Docs:* WP-0012/0013. *Capacidades:* CAP-13. *Etapa:* E2. *Obs:* sinónimo Guion/Script.
- **OBJ-053 · Storyboard** — *Def:* plan visual del guion (WP-0012). *Docs:* WP-0012. *Capacidades:* CAP-14. *Etapa:* E2.
- **OBJ-054 · Visual plan / Style guide** — *Def:* estilo y plan de recursos (WP-0012 C-15). *Docs:* WP-0012. *Capacidades:* CAP-15. *Etapa:* E2. *Obs:* no inventariado.

### Familia Publication

- **OBJ-060 · Asset / Resource (Recursos)** — *Def:* imágenes, clips, gráficos, música, SFX (WP-0012/0016). *Docs:* WP-0012/0016. *Capacidades:* CAP-16. *Etapa:* E3. *Obs:* sinónimo Recursos/Assets.
- **OBJ-061 · Voiceover (Locución)** — *Def:* pista de narración (WP-0012). *Docs:* WP-0012. *Capacidades:* CAP-17. *Etapa:* E3. *Obs:* sinónimo Locución/Voiceover.
- **OBJ-062 · Video** — *Def:* pieza editada/exportada/publicada (WP-0012/0013). *Docs:* WP-0012/0013. *Capacidades:* CAP-18, CAP-20. *Etapa:* E3/E4.
- **OBJ-063 · Packaging (título/miniatura)** — *Def:* empaquetado para el clic (WP-0012 C-21). *Docs:* WP-0012. *Capacidades:* CAP-21. *Etapa:* E4. *Obs:* no inventariado.
- **OBJ-064 · Publication metadata / SEO** — *Def:* descripción, tags, capítulos (WP-0012 C-22). *Docs:* WP-0012. *Capacidades:* CAP-22. *Etapa:* E4.
- **OBJ-065 · Rights / Licenses** — *Def:* licencias y atribuciones (WP-0012 C-23). *Docs:* WP-0012. *Capacidades:* CAP-23. *Etapa:* E4. *Obs:* ligado a Provenance.
- **OBJ-066 · Publication record** — *Def:* registro/URL de publicación (WP-0012 C-24). *Docs:* WP-0012. *Capacidades:* CAP-24. *Etapa:* E4. *Obs:* no inventariado.
- **OBJ-067 · Distribution / Clips** — *Def:* difusión y cortes (WP-0012 C-25). *Docs:* WP-0012. *Capacidades:* CAP-25. *Etapa:* E4. *Obs:* CAP-25 "Fuera del MVP" (WP-0013) → **candidato a desaparecer del MVP**.

### Familia Learning / Measurement

- **OBJ-070 · Metrics** — *Def:* datos de desempeño (WP-0012/0013). *Docs:* WP-0012/0013. *Capacidades:* CAP-26. *Etapa:* E5. *Invariantes:* INV-013, INV-020.
- **OBJ-071 · Feedback / Comments** — *Def:* respuesta de la audiencia (WP-0012 C-28). *Docs:* WP-0012. *Capacidades:* CAP-28. *Etapa:* E5. *Obs:* CAP-28 "Fuera del MVP" (WP-0013) → **candidato a desaparecer del MVP**; no inventariado.

### Familia Support Concepts

- **OBJ-080 · Entity** — *Def:* cosa identificable (WP-0009). *Docs:* WP-0009, WP-0019. *Obs:* **homonimia** con Entity (DDD, WP-0007).
- **OBJ-081 · Actor** — *Def:* entidad que actúa/participa (WP-0009). *Docs:* WP-0009. *Obs:* sinónimos Agent/persona de interés.
- **OBJ-082 · Event** — *Def:* suceso en tiempo/lugar (WP-0009). *Docs:* WP-0009, WP-0012. *Capacidades:* CAP-09. *Etapa:* E1.
- **OBJ-083 · Relationship** — *Def:* vínculo entre entidades/conceptos (WP-0009/0014). *Docs:* WP-0007/0009/0014. *Capacidades:* CAP-09, CAP-31. *Obs:* **ambiguo** (enlace vs primera clase).
- **OBJ-084 · Timeline (Cronología)** — *Def:* línea temporal de eventos (WP-0009/0012). *Docs:* WP-0009, WP-0012. *Capacidades:* CAP-09. *Etapa:* E1.
- **OBJ-085 · Contradiction** — *Def:* conflicto entre piezas de conocimiento (WP-0009/0012). *Docs:* WP-0009, WP-0012. *Capacidades:* CAP-09. *Etapa:* E1.
- **OBJ-086 · Collection** — *Def:* conjunto organizado de materiales (WP-0009). *Docs:* WP-0009. *Obs:* solapa con Case/Research como agrupador.
- **OBJ-087 · Criteria** — *Def:* reglas de selección/aceptación/clasificación (WP-0012/0013). *Docs:* WP-0012/0013. *Capacidades:* CAP-02, CAP-19.
- **OBJ-088 · Dependency** — *Def:* prerrequisito funcional entre capacidades (WP-0014). *Docs:* WP-0014. *Obs:* relación entre capacidades, no objeto de dominio "puro".

---

## 3. Vistas transversales (según «Incluir»)

> Listas descriptivas que referencian los OBJ del §2. No deciden pertenencia al modelo.

### 3.1 Objetos claramente recurrentes
OBJ-001 Research, OBJ-010 Knowledge, OBJ-011 Knowledge Base, OBJ-020 Evidence, OBJ-040 Provenance, OBJ-027 Source, OBJ-012 Hypothesis, OBJ-013 Conclusion, OBJ-005 Capability, OBJ-083 Relationship.

### 3.2 Objetos ambiguos
OBJ-015 Information (vs Knowledge), OBJ-026 Fact (umbral), OBJ-021 Evidence Item (granularidad), OBJ-030 Trust (no nombrado en WP-0009), OBJ-083 Relationship (enlace vs primera clase), OBJ-028 Document (tensión con ADR-0002).

### 3.3 Objetos candidatos a desaparecer
OBJ-004 Workspace (descartado, ADR-0001), **Document Repository** (descartado, ADR-0002 §6; sin OBJ propio por ser solo alternativa), OBJ-002 Case y OBJ-003 Investigation (subsumidos por Research), OBJ-028 Document (tensión con ADR-0002), OBJ-067 Distribution/Clips y OBJ-071 Feedback/Comments (CAP-25/CAP-28 "Fuera del MVP", WP-0013).

### 3.4 Objetos con nombres duplicados
- OBJ-023 Claim / OBJ-024 Assertion / OBJ-025 Statement.
- OBJ-042 Citation / OBJ-043 Reference.
- OBJ-029 Confidence / Certainty (familia incertidumbre).
- OBJ-084 Timeline / "Cronología".
- OBJ-052 Script / "Guion"; OBJ-060 Asset / "Recursos"; OBJ-061 Voiceover / "Locución".
- OBJ-001 Research / OBJ-002 Case / OBJ-003 Investigation (unidad operacional).
- **Homonimia:** OBJ-080 Entity (dominio) vs Entity (DDD).

### 3.5 Objetos definidos normativamente por ADR
- OBJ-001 Research — **ADR-0001** (unidad operacional).
- OBJ-011 Knowledge Base — **ADR-0002** (activo permanente).
- OBJ-004 Workspace — **ADR-0001** (descartado).
- Document Repository — **ADR-0002** (descartado).

### 3.6 Objetos definidos únicamente en Discovery (sin definición normativa ADR/ARCH)
La mayoría de los de WP-0009: OBJ-021 Evidence Item, OBJ-022 Observation, OBJ-023 Claim, OBJ-024 Assertion, OBJ-026 Fact, OBJ-014 Finding, OBJ-041 Metadata, OBJ-042 Citation, OBJ-043 Reference, OBJ-044 Annotation, OBJ-080 Entity, OBJ-081 Actor, OBJ-082 Event, OBJ-085 Contradiction, OBJ-086 Collection, etc. (Evidence, Knowledge, Provenance sí tienen respaldo en ARCH-0002/ADR.)

---

## 4. Observaciones (descriptivas)

- El **núcleo normativo** (Research, Knowledge Base, Evidence, Knowledge, Provenance) está respaldado por ADR-0001/0002 y ARCH-0002; el resto procede de Discovery (sin definición normativa).
- Los **conflictos** (duplicados, ambiguos, homonimia, tensión Document) coinciden con WP-0019/WP-0024; se reafirman aquí a nivel de objeto.
- Los **candidatos a desaparecer** se apoyan en decisiones existentes (ADR descartes; CAP "Fuera del MVP" de WP-0013), no en juicio propio.
- Este inventario es **insumo directo de RFC-0002**, que decidirá qué objetos entran al modelo, su ownership y relaciones — decisiones **fuera del alcance** de este documento.
- Todo deriva de las fuentes permitidas; **no** se ha decidido, definido ni interpretado nada.

---

## 5. Referencias cruzadas

- ARCH-0002 · `docs/architecture/ARCH-0002-Domain-Philosophy.md`
- ADR-0001 · `docs/adr/ADR-0001-Research-is-the-Operational-Unit.md`
- ADR-0002 · `docs/adr/ADR-0002-Knowledge-Accumulation-is-the-Core-Value.md`
- WP-0009 · `docs/research/DOMAIN-ONTOLOGY-RESEARCH.md`
- WP-0013 · `docs/research/MVP-CAPABILITY-INVENTORY.md`
- WP-0014 · `docs/research/CAPABILITY-DEPENDENCY-MAP.md`
- WP-0016 · `docs/research/KNOWLEDGE-ASSET-INVENTORY.md`
- WP-0018 · `docs/research/RESEARCH-LIFECYCLE-EXTRACTION.md`
- WP-0019 · `docs/research/DISCOVERY-TO-DOMAIN-MAPPING.md`
- WP-0021 · `docs/research/DOMAIN-INVARIANT-EXTRACTION.md`
- WP-0024 · `docs/research/UBIQUITOUS-LANGUAGE-EXTRACTION.md`
- DS-0004 · `docs/research/RESEARCH-LIFECYCLE-TRACEABILITY.md`
- DS-0006 · `docs/spec/RESEARCH-LIFECYCLE-ACCEPTANCE-CRITERIA.md`

---

_Fin del inventario. Documento exclusivamente descriptivo: no decide el modelo, no define entidades/agregados/ownership/relaciones/estados, no propone comandos ni arquitectura y no interpreta el dominio. Entrada directa para RFC-0002 — Domain Model._
