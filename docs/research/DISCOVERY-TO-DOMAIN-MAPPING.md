# DISCOVERY TO DOMAIN MAPPING — DocumentaryAI (WP-0019)

| Campo | Valor |
|---|---|
| **Document ID** | RES-DISCOVERY-TO-DOMAIN-MAPPING |
| **Title** | Discovery to Domain Mapping — DocumentaryAI |
| **Status** | Draft (mapping) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | WP-0007…WP-0018; ARCH-0002 (ver §7) |

> **Documento puente, exclusivamente descriptivo y trazable.** Inventaria los conceptos descubiertos en WP-0007…WP-0018 como insumo para la futura redacción de **RFC-0002 — Domain Model**.
> **No** propone arquitectura, **no** diseña entidades, **no** crea relaciones nuevas, **no** modifica documentos existentes y **no** decide qué entra o sale del dominio. Las "naturalezas" y las marcas son **lecturas tentativas** derivadas de la documentación, no decisiones.

---

## 1. Método y leyenda

- **Fuente:** conceptos que aparecen en WP-0007…WP-0018 (principal fuente de definiciones: WP-0009; ejes epistémicos: WP-0010/0011; capacidades/artefactos: WP-0012/0013/0014/0016/0018).
- **Definiciones:** resumidas de la documentación; no se introducen definiciones nuevas.
- **Naturaleza (tentativa, múltiple):**
  - **D** — Concepto permanente del dominio (candidato).
  - **P** — Concepto de proceso.
  - **A** — Activo de conocimiento.
  - **C** — Capacidad.
  - **T** — Artefacto.
  - **M** — Metadato.
- Un concepto puede llevar **varias** etiquetas; la asignación es descriptiva, **no** normativa, y **no** decide su pertenencia al dominio.

---

## 2. Inventario de conceptos

### 2.1 Unidades epistémicas / de conocimiento

| Concepto | Origen | Definición resumida | Naturaleza |
|---|---|---|---|
| Evidence (Evidencia) | WP-0007/0009/0010/0011 | Información/material que apoya o refuta una afirmación; rol relacional | D, A |
| Evidence Item | WP-0009 | Unidad discreta e identificable de evidencia | D, A |
| Observation (Observación) | WP-0009/0012 | Constatación directa previa a interpretación | D, A |
| Claim (Afirmación) | WP-0009/0010/0011 | Enunciado propuesto como verdadero, sujeto a respaldo | D, A |
| Assertion | WP-0009 | Acto/proposición afirmada (atribuible a un emisor) | D, A |
| Statement | WP-0010 | Enunciado | A |
| Fact (Hecho) | WP-0009/0010/0011 | Afirmación verificable tenida por cierta | D, A |
| Finding (Hallazgo) | WP-0009/0010/0012 | Resultado de un análisis | A |
| Hypothesis (Hipótesis) | WP-0009/0010/0012/0013 | Explicación tentativa contrastable | D, A |
| Conclusion (Conclusión) | WP-0009/0010 | Afirmación final del razonamiento | A, D |
| Knowledge (Conocimiento) | WP-0009/0010/0011 | Información estructurada y justificada | D, A |
| Information (Información) | WP-0011 | Nivel previo al conocimiento (DIKW) | A |
| Interpretation (Interpretación) | WP-0007/0010/0011 | Valoración mutable frente al hecho constatado | P, D |
| Justification (Justificación) | WP-0010/0011 | Respaldo que distingue conocimiento de creencia | D, P |

### 2.2 Modelo del mundo

| Concepto | Origen | Definición resumida | Naturaleza |
|---|---|---|---|
| Entity (Entidad, dominio) | WP-0009 | Cosa identificable (persona, lugar, objeto…) | D |
| Actor | WP-0009 | Entidad que actúa/participa (agente) | D |
| Event (Evento) | WP-0009 | Suceso en tiempo/lugar | D |
| Relationship (Relación) | WP-0007/0009/0014 | Vínculo entre entidades/conceptos | D |
| Timeline (Cronología) | WP-0009/0012 | Línea temporal de eventos | A, D |
| Contradiction (Contradicción) | WP-0009/0012 | Conflicto entre piezas de conocimiento | A, D |

### 2.3 Fuentes, procedencia y descripción

| Concepto | Origen | Definición resumida | Naturaleza |
|---|---|---|---|
| Source (Fuente) | WP-0009/0010 | Origen del que procede info/material | D, A |
| Document (Documento) | WP-0007/0009 | Unidad de contenido registrada; portador | A, T |
| Collection (Colección) | WP-0009 | Conjunto organizado de materiales | A |
| Provenance (Procedencia) | WP-0007/0009/0011 | Origen e historia de un material/afirmación | D, M |
| Metadata (Metadatos) | WP-0009 | Datos que describen otros datos | M |
| Annotation (Anotación) | WP-0009 | Información añadida por un analista | A, M |
| Citation (Cita) | WP-0009 | Indicación formal de la fuente | M, A |
| Reference (Referencia) | WP-0009 | Apuntador a un recurso | M |

### 2.4 Incertidumbre y fiabilidad

| Concepto | Origen | Definición resumida | Naturaleza |
|---|---|---|---|
| Confidence (Confianza) | WP-0010/0011/0013 | Grado de certeza graduable | M, D |
| Certainty (Certeza) | WP-0010 | Estado de certeza (cuasi binario) | M |
| Uncertainty (Incertidumbre) | WP-0010/0013 | Falta de certeza | M |
| Trust (Fiabilidad/credibilidad) | WP-0011 | Fiabilidad de fuente / credibilidad de info | M |
| Belief (Creencia) | WP-0010 | Creencia (vs conocimiento justificado) | (epistémico) |
| Truth (Verdad) | WP-0010 | Verdad (vs justificación) | (epistémico) |

### 2.5 Proceso / ciclo de vida

| Concepto | Origen | Definición resumida | Naturaleza |
|---|---|---|---|
| Research / Research project | ARCH-0002/WP-0018 | Proceso de investigación (actividad central) | P, D |
| Investigation (Investigación) | WP-0009 | Proceso de indagación | P, D |
| Case (Caso) | WP-0009 | Asunto investigado (contenedor) | D, P |
| Lifecycle stages (Etapas) | WP-0018 | Investigación→Narrativa→Producción→Publicación→Aprendizaje | P |
| Learning / Lessons learned | WP-0012/0013/ARCH-0002 | Aprendizaje reutilizable del ciclo | A, P |
| Pattern (Patrón) | WP-0010/0016 | Patrón epistémico/de investigación reutilizable | A |
| Criteria (Criterios) | WP-0012/0013 | Reglas de selección/aceptación/clasificación | P |
| Dependency (Dependencia) | WP-0014 | Prerrequisito funcional entre capacidades | (relación/meta) |

### 2.6 Capacidades

| Concepto | Origen | Definición resumida | Naturaleza |
|---|---|---|---|
| Capability (Capacidad) | WP-0012/0013/0014 | Algo que el proceso/sistema debe poder hacer | C |
| (33 capacidades CAP-01…CAP-33) | WP-0013 | Capacidades concretas del MVP | C |

### 2.7 Artefactos de producción

| Concepto | Origen | Definición resumida | Naturaleza |
|---|---|---|---|
| Idea / Topic / Objective | WP-0012 | Idea, tema y objetivos del proyecto | T, P |
| Source list / Notes | WP-0012 | Lista de fuentes y material recopilado | T, A |
| Narrative concept / Structure | WP-0012 | Ángulo y estructura/escaleta | T, P |
| Script (Guion) | WP-0012/0013/ARCH-0002 | Texto narrado del documental | T |
| Storyboard | WP-0012 | Plan visual del guion | T |
| Visual plan / Style guide | WP-0012 | Estilo y plan de recursos | T |
| Asset (Recursos) | WP-0012/0016 | Imágenes, clips, gráficos, música, SFX | T |
| Voiceover (Locución) | WP-0012 | Pista de narración | T |
| Video (Vídeo final) | WP-0012/0013 | Pieza exportada/publicada | T |
| Packaging (Título/miniatura) | WP-0012 | Empaquetado para el clic | T |
| Publication metadata / SEO | WP-0012 | Descripción, tags, capítulos | M, T |
| Rights / Licenses | WP-0012 | Licencias y atribuciones | M, T |
| Metrics (Métricas) | WP-0012/0013 | Datos de desempeño | A, T |
| Feedback / Comments | WP-0012 | Respuesta de la audiencia | T, A |
| Distribution / Clips | WP-0012 | Difusión y cortes | T, P |

### 2.8 Construcciones analíticas / técnicas (no de dominio)

| Concepto | Origen | Definición resumida | Naturaleza |
|---|---|---|---|
| Document/Case/Evidence/Knowledge-centric | WP-0007 | Enfoques de modelado comparados | (analítico) |
| Aggregate Root / Bounded Context / Value Object / Entity (DDD) | WP-0007 (y ARCH-0002 §11 los excluye) | Construcciones de modelado DDD | (técnico) |
| Knowledge graph | ARCH-0002 §8 (lo excluye) | Representación en grafo | (técnico) |
| DIKW | WP-0009/0010 | Jerarquía dato-info-conocimiento-sabiduría | (marco) |
| Ubiquitous Language | AC-0003 | Lenguaje propio a definir por el Architect | (gobernanza/meta) |

---

## 3. Duplicidades semánticas

> Conceptos con significado igual o muy solapado (constatación; no se fusionan).

- **Claim ≈ Assertion ≈ Statement** — proposición afirmada sujeta a respaldo; matices (acto vs proposición vs "no probado").
- **Certainty ≈ Confidence** (y **Uncertainty** como inverso) — grado de certeza.
- **Citation ≈ Reference** — apuntador a la fuente; ambos solapan con **Provenance**.
- **Case ≈ Investigation** — asunto (contenedor) vs proceso (indagación); fronteras difusas (y solapan con **Research**).
- **Evidence ≈ Evidence Item** — diferencia de granularidad, no de naturaleza.
- **Trust ≈ Reliability/Credibility** — fiabilidad de fuente / credibilidad de información.
- **Knowledge ↔ Information** — frontera difusa (DIKW).
- **Fact ↔ Claim corroborado** — umbral variable para "hecho".

---

## 4. Conceptos equivalentes con nombres distintos

> Mismo referente, distinta etiqueta según el documento.

| Etiqueta(s) | Equivalente | Origen |
|---|---|---|
| Statement / Assertion / Claim | misma idea de "afirmación" | WP-0009/0010 |
| Certainty / Confidence | grado de certeza | WP-0010/0011/0013 |
| Citation / Reference | apuntador a fuente | WP-0009 |
| Cronología / Timeline | línea temporal | WP-0009/0012 |
| Recursos / Assets | material audiovisual | WP-0012/0016 |
| Guion / Script | guion del documental | WP-0012/0013 |
| Locución / Voiceover | narración | WP-0012 |
| Empaquetado / Packaging | título+miniatura | WP-0012 |
| Reliability + Credibility / Trust | fiabilidad/credibilidad | WP-0010/0011 |
| Actor / Agent / Persona de interés | entidad que actúa | WP-0009/0010 |
| Lessons learned / Learning | aprendizaje reutilizable | WP-0012/0013 |

> Caso especial de **homonimia** (mismo nombre, distinto sentido), no equivalencia: **Entity (dominio)** = cosa del mundo (WP-0009) vs **Entity (DDD)** = construcción de modelado (WP-0007). Se señala para evitar confusión.

---

## 5. Conceptos que probablemente no formen parte del modelo del MVP

> **Señalización descriptiva, no decisión.** Cada marca se apoya en documentación existente (ARCH-0002 / WP-0013). El Principal Architect decide.

| Concepto | Motivo (trazable) |
|---|---|
| Aggregate Root, Bounded Context, Value Object, Entity (DDD) | Construcciones de modelado; **ARCH-0002 §11** las excluye explícitamente del nivel filosófico (corresponden a artefactos posteriores). |
| Knowledge graph | **ARCH-0002 §8** declara que DocumentaryAI **no es** un knowledge graph. |
| Document/Case/Evidence/Knowledge-centric | Enfoques **analíticos** de WP-0007 para comparar; no conceptos del dominio. |
| DIKW | **Marco** de referencia (WP-0009/0010), no un concepto del dominio. |
| Truth, Belief | Conceptos **epistemológicos** de fondo (WP-0010); aparecen como ejes de contraste, no como unidades del dominio. |
| Information | Frontera difusa con Knowledge (WP-0011); su distinción puede no requerir modelado propio. |
| Distribution / Clips, Feedback / Comments | Asociados a **CAP-25 y CAP-28**, clasificadas **"Fuera del MVP"** en **WP-0013**. |
| Ubiquitous Language | Concepto de **gobernanza/meta** (AC-0003), no del dominio. |

> Estas marcas son **candidatas** a quedar fuera; no se elimina ni decide nada aquí.

---

## 6. Observaciones (descriptivas)

- El grueso de conceptos del dominio proviene de **WP-0009**; los **atributos epistémicos** (confianza, justificación, interpretación) de **WP-0010/0011**; las **capacidades y artefactos** de **WP-0012/0013/0014/0016/0018**.
- Hay un **núcleo recurrente y consensuado** (Evidence, Provenance, Knowledge, Hypothesis, Interpretation, Relationship, Source) que coincide con los consensos altos de **WP-0011** y con los principios de **ARCH-0002** (AP-001 Knowledge First, AP-003 Evidence Before Knowledge, AP-004 Traceability).
- Las **duplicidades** y **equivalencias** señaladas (§3/§4) son el material principal que el lenguaje ubicuo (AC-0003) deberá unificar.
- Las naturalezas múltiples (p. ej. Evidence como D+A; Provenance como D+M) reflejan que **un mismo concepto** puede tener varios roles; aquí solo se constata, no se resuelve.
- Todo deriva de los documentos citados; **no** se ha creado ningún concepto, relación ni decisión.

---

## 7. Referencias cruzadas

- WP-0007 · `docs/architecture/Evidence-Centric-Domain-Research.md`
- WP-0009 · `docs/research/DOMAIN-ONTOLOGY-RESEARCH.md`
- WP-0010 · `docs/research/EPISTEMIC-DOMAIN-PATTERN-RESEARCH.md`
- WP-0011 · `docs/research/DOMAIN-EVIDENCE-SYNTHESIS-MATRIX.md`
- WP-0012 · `docs/research/YOUTUBE-DOCUMENTARY-PRODUCTION-CAPABILITY-MAP.md`
- WP-0013 · `docs/research/MVP-CAPABILITY-INVENTORY.md`
- WP-0014 · `docs/research/CAPABILITY-DEPENDENCY-MAP.md`
- WP-0015 · `docs/research/DISCOVERY-INDEX.md`
- WP-0016 · `docs/research/KNOWLEDGE-ASSET-INVENTORY.md`
- WP-0017 · `docs/research/MVP-CAPABILITY-TRACEABILITY-MATRIX.md`
- WP-0018 · `docs/research/RESEARCH-LIFECYCLE-EXTRACTION.md`
- ARCH-0002 · `docs/architecture/ARCH-0002-Domain-Philosophy.md`

---

_Fin del mapeo. Documento exclusivamente descriptivo y trazable: no propone arquitectura, no diseña entidades, no crea relaciones nuevas, no modifica documentos existentes y no decide qué entra o sale del dominio. Insumo para RFC-0002 — Domain Model._
