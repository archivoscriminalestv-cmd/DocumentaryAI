# UBIQUITOUS LANGUAGE EXTRACTION — DocumentaryAI (WP-0024)

| Campo | Valor |
|---|---|
| **Document ID** | RES-UBIQUITOUS-LANGUAGE-EXTRACTION |
| **Title** | Ubiquitous Language Extraction — DocumentaryAI |
| **Status** | Draft (extraction / terminology audit) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | ARCH-0002; ADR-0001; ADR-0002; WP-0007…WP-0022; DS-0004…DS-0007 |

> **Extracción y auditoría terminológica, exclusivamente recopilatoria.** Reúne los términos de dominio **usados** en el material existente.
> **No** normaliza el vocabulario, **no** propone definiciones nuevas, **no** diseña el lenguaje ubicuo y **no** toma decisiones arquitectónicas. Las definiciones se **derivan/citan** de los documentos; los conflictos se **señalan**, no se resuelven.
> Evidencia para **RFC-0002 — Domain Model**.

---

## 1. Método y leyenda

- **Fuentes:** ARCH-0002, ADR-0001, ADR-0002, WP-0007…WP-0022, DS-0004…DS-0007.
- **Campos por término:** término · definición (literal/resumida derivada) · documentos donde aparece · sinónimos usados · posibles conflictos terminológicos.
- **Prioridad de fuente para la definición:** cuando un término tiene definición **normativa** en ADR/ARCH, se cita esa; en caso contrario, la de WP-0009 (ontología) u otros.
- Esta auditoría **no** unifica sinónimos ni elige término canónico (eso corresponde al lenguaje ubicuo que definirá el Principal Architect, AC-0003).

---

## 2. Núcleo del dominio (términos normativos de los ADR)

| Término | Definición (derivada/citada) | Documentos | Sinónimos usados | Posibles conflictos |
|---|---|---|---|---|
| **Research** | "La unidad operacional de DocumentaryAI"; "una investigación delimitada en el tiempo y en el objetivo"; "transformar información externa en conocimiento reutilizable"; "no representa el conocimiento permanente" (ADR-0001 §2). | ADR-0001, ADR-0002, WP-0018, WP-0020, DS-0004 | Investigation, Case (WP-0009); "Research project" (ARCH-0002) | Solapa con **Investigation** y **Case** (WP-0009); ADR-0001 fija "Research" como término operacional → los otros quedan como sinónimos/antecedentes |
| **Knowledge Base** | "Constituye el activo permanente de DocumentaryAI"; "toda Research existe para incrementar la Knowledge Base" (ADR-0002 §2). | ADR-0002, WP-0020 | — | Relación estrecha con **Knowledge** (contenido vs almacén permanente); no confundir con **Document Repository** (descartado) |
| **Knowledge** | "Información estructurada, contextualizada y justificada"; "no equivale a documentos" (WP-0009; ARCH-0002 §5). Producto primario (AP-001). | ARCH-0002, WP-0009/0010/0011, WP-0016, ADR-0002 | "reusable knowledge", "domain understanding" (ARCH-0002 §6) | Frontera difusa con **Information**; distinto de **Knowledge Base** (Knowledge = activo; Knowledge Base = patrimonio que lo acumula) |
| **Workspace** | Alternativa considerada y **descartada** como unidad operacional: "espacio organizativo. No describe un proceso" (ADR-0001 §6). | ADR-0001 | — | Descartado; no es término operacional |
| **Document Repository** | Alternativa considerada y **descartada** como activo: "El dominio no gestiona documentos. Gestiona conocimiento" (ADR-0002 §6). | ADR-0002 | — | Descartado; en tensión con la idea (rechazada) de gestionar documentos |

---

## 3. Unidades epistémicas

| Término | Definición (derivada) | Documentos | Sinónimos | Posibles conflictos |
|---|---|---|---|---|
| **Evidence** | Información/material que apoya o refuta una afirmación; tratada como **rol relacional**; "Evidence precedes interpretation" (ARCH-0002 AP-003; WP-0009/0011). | ARCH-0002, WP-0007/0009/0010/0011, DS-0004 | "supporting data", "proof" (más fuerte) | Material vs relación de apoyo; "evidence" (incontable) vs **Evidence Item** (discreto) |
| **Evidence Item** | Unidad discreta e identificable de evidencia (WP-0009). | WP-0009 | exhibit, piece of evidence | Granularidad indefinida; solapa con Evidence y Document |
| **Observation** | Constatación directa previa a la interpretación (WP-0009). | WP-0009, WP-0012, DS-0004 | datum, measurement | Neutralidad discutida (¿ya interpretada?) |
| **Claim** | Enunciado propuesto como verdadero, sujeto a respaldo (WP-0009). | WP-0009/0010/0011 | Assertion, Statement | Casi sinónimo de Assertion/Statement (matiz "no probado") |
| **Assertion** | Acto/proposición afirmada, atribuible a un emisor (WP-0009). | WP-0009 | Claim, Statement, triple (RDF) | Acto vs proposición; intercambiable con Claim |
| **Statement** | Enunciado (eje Statement↔Claim, WP-0010). | WP-0010 | Claim, Assertion | Sin matiz propio consistente |
| **Fact** | Afirmación verificable tenida por cierta; umbral variable por disciplina (WP-0009/0010). | WP-0009/0010/0011 | "ground truth", "verified statement" | Frontera con **Claim corroborado**; umbral no definido |
| **Finding** | Resultado de un análisis (WP-0009). | WP-0009/0010/0012 | result, determination | Intermedio vs conclusivo (frontera con Conclusion) |
| **Hypothesis** | Explicación tentativa contrastable (WP-0009/0010). | WP-0009/0010/0012/0013 | conjecture, "working hypothesis" | "hypothesis" vs "theory" (uso laxo) |
| **Conclusion** | Afirmación final del razonamiento (WP-0009). | WP-0009/0010 | determination, judgment | Frontera con Finding; grado de finalidad |
| **Interpretation** | Valoración mutable frente al hecho constatado (separación hecho↔interpretación) (WP-0007/0010/0011). | WP-0007/0010/0011, WP-0019 | — | Pareja con Fact (constatación vs interpretación) |
| **Justification** | Respaldo que distingue conocimiento de creencia (WP-0010/0011). | WP-0010/0011 | — | Solapa con Evidence/Provenance como "respaldo" |
| **Information** | Nivel previo al conocimiento (DIKW) (WP-0011). | WP-0011 | — | Frontera difusa con Knowledge |

---

## 4. Fuentes, procedencia y descripción

| Término | Definición (derivada) | Documentos | Sinónimos | Posibles conflictos |
|---|---|---|---|---|
| **Source** | Origen del que procede info/material (WP-0009). | WP-0009/0010, DS-0004 | origin, informant, primary/secondary source | Origen (autor/agente) vs documento portador |
| **Document** | Unidad de contenido registrada; portador (WP-0009). "knowledge is not equivalent to documents" (ARCH-0002 §5). | WP-0007/0009, WP-0012 | record, file, artifact | El dominio "gestiona conocimiento, no documentos" (ADR-0002) → tensión con tratar Document como central |
| **Provenance** | Origen e historia de un material/afirmación (WP-0009). "Traceability… never optional" (ARCH-0002 AP-004). | ARCH-0002, WP-0007/0009/0011, WP-0016 | lineage, chain of custody, pedigree | Alcance (origen vs historia completa); solapa con Metadata/Citation |
| **Metadata** | Datos que describen otros datos (WP-0009). | WP-0009 | attributes, properties, tags | Solapa con Provenance/Annotation |
| **Annotation** | Información añadida por un analista (WP-0009). | WP-0009 | note, tag, label | Dato vs interpretación |
| **Citation** | Indicación formal de la fuente (WP-0009). | WP-0009 | reference, attribution | Citation vs Reference según estilo |
| **Reference** | Apuntador a un recurso (WP-0009). | WP-0009 | link, pointer | Reference vs Citation; vs Relationship |
| **Collection** | Conjunto organizado de materiales (WP-0009). | WP-0009 | corpus, dataset, fonds | Solapa con Case/Research como agrupador |

---

## 5. Modelo del mundo

| Término | Definición (derivada) | Documentos | Sinónimos | Posibles conflictos |
|---|---|---|---|---|
| **Entity** | Cosa identificable (persona, lugar, objeto…) (WP-0009). | WP-0009, WP-0019 | object, node, thing, named entity | **Homonimia**: Entity (dominio) vs Entity (DDD, WP-0007) |
| **Actor** | Entidad que actúa/participa (WP-0009). | WP-0009 | agent, party, person of interest | Persona vs agente genérico; vs Agent (PROV) |
| **Event** | Suceso en tiempo/lugar (WP-0009). | WP-0009, WP-0012 | incident, occurrence, activity | Hecho vs afirmación de hecho; granularidad |
| **Relationship** | Vínculo entre entidades/conceptos (WP-0009/0014). | WP-0007/0009/0014 | link, edge, predicate, association | Enlace simple vs relación de primera clase |
| **Timeline (Cronología)** | Línea temporal de eventos (WP-0009/0012). | WP-0009, WP-0012 | cronología | — |
| **Contradiction** | Conflicto entre piezas de conocimiento (WP-0009/0012). | WP-0009, WP-0012 | — | — |

---

## 6. Incertidumbre, fiabilidad y aprendizaje

| Término | Definición (derivada) | Documentos | Sinónimos | Posibles conflictos |
|---|---|---|---|---|
| **Confidence** | Grado de certeza graduable (WP-0010/0011/0013). | WP-0010/0011/0013 | — | ≈ Certainty (matiz binario/graduable) |
| **Certainty** | Estado de certeza (cuasi binario) (WP-0010). | WP-0010 | — | ≈ Confidence |
| **Uncertainty** | Falta de certeza (WP-0010/0013). | WP-0010/0013 | — | Inverso de Confidence |
| **Trust** | Fiabilidad de fuente / credibilidad de info (WP-0011). | WP-0010/0011 | reliability, credibility | No nombrado como "Trust" en WP-0009; aparece como fiabilidad/credibilidad |
| **Learning / Lessons learned** | Aprendizaje reutilizable del ciclo; "Every completed research project must improve the platform" (ARCH-0002 §6). | ARCH-0002, WP-0012/0013, ADR-0002 | "lessons learned", "accumulated learning" | — |
| **Pattern** | Patrón epistémico/de investigación reutilizable (WP-0010/0016). | WP-0010, WP-0016 | "research pattern" | — |

---

## 7. Proceso, capacidades y artefactos (términos de ciclo)

| Término | Definición (derivada) | Documentos | Sinónimos | Posibles conflictos |
|---|---|---|---|---|
| **Capability** | Algo que el proceso/sistema debe poder hacer (WP-0012/0013/0014). "Capabilities endure. Implementations evolve" (ARCH-0002 AP-006). | ARCH-0002, WP-0012/0013/0014 | — | — |
| **Lifecycle (Etapas)** | Investigación→Narrativa→Producción→Publicación→Aprendizaje (WP-0018). | WP-0018, DS-0004 | "research lifecycle" | — |
| **Case** | Asunto investigado (contenedor) (WP-0009). | WP-0009 | matter, dossier | Subsumido por **Research** (ADR-0001); conflicto Case vs Research |
| **Investigation** | Proceso de indagación (WP-0009). | WP-0009 | inquiry, probe | Subsumido por **Research** (ADR-0001) |
| **Artifact / Knowledge Asset** | Producto generado por una capacidad / tipo de activo de conocimiento (WP-0012/0016). | WP-0012, WP-0016 | asset | "Artifact" (producción) vs "Knowledge Asset" (conocimiento) |
| **Script (Guion), Storyboard, Asset (Recursos), Video, Metrics** | Artefactos de producción del ciclo (WP-0012/0013). | WP-0012/0013 | guion/script; recursos/assets; locución/voiceover | Términos ES/EN intercambiados (ver WP-0019 §4) |

---

## 8. Conflictos terminológicos destacados (auditoría)

> Señalización, sin resolver (la unificación corresponde al lenguaje ubicuo, AC-0003).

1. **Research / Investigation / Case:** ADR-0001 fija **Research** como unidad operacional; **Investigation** y **Case** (WP-0009) quedan como términos previos/sinónimos. Conviene declararlo explícitamente en el lenguaje ubicuo.
2. **Knowledge / Knowledge Base:** Knowledge = activo/contenido; Knowledge Base = activo **permanente** que lo acumula (ADR-0002). Relación estrecha; riesgo de uso intercambiable.
3. **Claim / Assertion / Statement:** sinónimos con matices no estabilizados.
4. **Confidence / Certainty / Uncertainty / Trust:** familia de "grado de certeza/fiabilidad" sin término canónico.
5. **Fact / Claim corroborado:** umbral de "hecho" no definido.
6. **Citation / Reference / Provenance:** solapamiento en "apuntar a la fuente / registrar origen".
7. **Entity (dominio) vs Entity (DDD):** **homonimia** con sentidos distintos.
8. **Document:** término usado, pero ADR-0002 declara que el dominio "no gestiona documentos"; tensión entre el término y la decisión.
9. **Sinónimos ES/EN** en artefactos de producción (guion/script, recursos/assets, locución/voiceover, etc.).
10. **(Meta, no de dominio)** Nombre de RFC-0002: ADR-0001 lo cita como *"Core Domain Rules"* y ADR-0002/índice como *"Domain Model"* — divergencia de nombre de documento, señalada para unificación.

---

## 9. Observaciones (descriptivas)

- Los términos con **definición normativa** (Research, Knowledge Base) provienen de ADR-0001/0002; el resto, de la ontología/Discovery (WP-0009 y sucesivos).
- La mayor parte de los **conflictos** ya estaban señalados en WP-0019 (§3/§4); este documento los **reafirma** y añade los derivados de los ADR (Research vs Case/Investigation; Document vs "no gestiona documentos").
- Esta extracción es **insumo directo** para que RFC-0002 fije el **lenguaje ubicuo** (AC-0003), eligiendo términos canónicos y resolviendo los conflictos del §8.
- Todo deriva de las fuentes citadas; **no** se ha normalizado, definido ni decidido nada.

---

## 10. Referencias cruzadas

- ARCH-0002 · `docs/architecture/ARCH-0002-Domain-Philosophy.md`
- ADR-0001 · `docs/adr/ADR-0001-Research-is-the-Operational-Unit.md`
- ADR-0002 · `docs/adr/ADR-0002-Knowledge-Accumulation-is-the-Core-Value.md`
- WP-0009 · `docs/research/DOMAIN-ONTOLOGY-RESEARCH.md`
- WP-0019 · `docs/research/DISCOVERY-TO-DOMAIN-MAPPING.md`
- WP-0020 · `docs/research/AGGREGATE-CANDIDATE-ANALYSIS.md`
- WP-0021 · `docs/research/DOMAIN-INVARIANT-EXTRACTION.md`
- DS-0004 · `docs/research/RESEARCH-LIFECYCLE-TRACEABILITY.md`
- DS-0006 · `docs/spec/RESEARCH-LIFECYCLE-ACCEPTANCE-CRITERIA.md`

---

_Fin de la extracción. Documento exclusivamente de extracción y auditoría terminológica: no normaliza vocabulario, no propone definiciones nuevas, no diseña el lenguaje ubicuo y no toma decisiones arquitectónicas. Evidencia para RFC-0002 — Domain Model._
