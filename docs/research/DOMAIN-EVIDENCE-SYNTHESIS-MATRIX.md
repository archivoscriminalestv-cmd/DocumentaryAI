# DOMAIN EVIDENCE SYNTHESIS MATRIX — DocumentaryAI (WP-0011)

| Campo | Valor |
|---|---|
| **Document ID** | RES-EVIDENCE-SYNTHESIS |
| **Title** | Domain Evidence Synthesis Matrix — DocumentaryAI |
| **Status** | Draft (research synthesis) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | `docs/architecture/Evidence-Centric-Domain-Research.md` (WP-0007), `docs/research/DOMAIN-ONTOLOGY-RESEARCH.md` (WP-0009), `docs/research/EPISTEMIC-DOMAIN-PATTERN-RESEARCH.md` (WP-0010) |

> **Documento de síntesis.** Consolida exclusivamente la evidencia de WP-0007, WP-0009 y WP-0010 en una matriz de trazabilidad de apoyo a la redacción de **ARCH-0002 — Domain Philosophy**.
> **No** incorpora fuentes ni conocimiento nuevos, **no** resuelve contradicciones, **no** elige terminología, **no** prioriza disciplinas, **no** propone ontología/arquitectura ni elementos DDD y **no** decide.

---

## 1. Objetivo

Reducir la carga de consulta del Principal Architect durante la redacción de ARCH-0002, ofreciendo una **vista única y trazable** de qué dijo cada Work Package de investigación sobre cada tema del dominio, con su nivel de consenso y observaciones.

La síntesis es **derivada**: cada celda remite a lo ya escrito en los tres documentos fuente; no añade afirmaciones nuevas.

---

## 2. Alcance

- Se analizan **solo** los tres documentos fuente (§3). No se introduce ninguna fuente externa.
- Se cubren los **23 temas** requeridos por el WP más los **temas recurrentes adicionales** detectados de forma consistente en los tres documentos.
- Para cada tema: tratamiento en WP-0007 / WP-0009 / WP-0010, **nivel de consenso** y **observaciones**.
- Fuera de alcance: cualquier decisión, principio, ontología, resolución de contradicciones o elección terminológica.

**Leyenda de consenso:**
- **Alto** — los tres WP coinciden en la idea esencial.
- **Medio** — coincidencia parcial, o tratado de forma comparable en 2 de 3.
- **Bajo** — tratado de forma divergente o solo de pasada.
- **1 fuente** — abordado de forma sustantiva en un único WP.

---

## 3. Fuentes analizadas

| Ref | Work Package | Documento | Naturaleza del tratamiento |
|---|---|---|---|
| **WP-0007** | Evidence-Centric Domain Research | `docs/architecture/Evidence-Centric-Domain-Research.md` | Enfoques "centric" (document/case/evidence/knowledge), riesgos de Evidence como Aggregate Root, procedencia, separación hecho↔interpretación. |
| **WP-0009** | Domain Ontology Research | `docs/research/DOMAIN-ONTOLOGY-RESEARCH.md` | Definiciones por concepto (24), variantes, ambigüedades, diferencias entre disciplinas. |
| **WP-0010** | Epistemic Domain Pattern Research | `docs/research/EPISTEMIC-DOMAIN-PATTERN-RESEARCH.md` | Patrones del ciclo de conocimiento en 9 disciplinas y comparativa transversal de 8 ejes. |

---

## 4. Matriz de trazabilidad

> Síntesis de lo expresado por cada WP. "—" = no tratado de forma explícita/comparable en ese WP.

### 4.1 Temas requeridos

| Tema | WP-0007 | WP-0009 | WP-0010 | Consenso | Observaciones |
|---|---|---|---|---|---|
| **Evidence** | Concepto central; evidencia como **rol relacional** (material vs relación de apoyo); riesgos como Aggregate Root | Definida: info/material que apoya o refuta; ambigüedad material↔relación; "proof" más fuerte | Evidencia como **rol respecto a una hipótesis**; eje Observation↔Evidence y Evidence↔Fact | **Alto** | Coinciden en la naturaleza **relacional** de la evidencia; persiste la ambigüedad material vs relación |
| **Observation** | Implícito (separación hecho↔interpretación) | Definida: constatación directa previa a interpretación | Observación por disciplina; eje Observation↔Evidence | **Medio** | Idea común: constatación previa a su uso como evidencia |
| **Source** | Procedencia como activo de primer orden | Definida: origen vs portador; fiabilidad separada | Fuente en inteligencia/periodismo (fiabilidad vs credibilidad) | **Medio** | Ambigüedad origen↔documento portador recurrente |
| **Document** | Enfoque document-centric (contenedor/portador) | Definido: contenedor vs contenido; "record" | Artefacto (forense), documento como evidencia (periodismo) | **Medio** | El documento como **portador**, no como verdad en sí |
| **Information** | — | Aparece dentro de Knowledge (DIKW), no como concepto aislado | Tema eje: transformación información→conocimiento (DIKW) | **Bajo** | Frontera información↔conocimiento difusa; no aislado en WP-0009 |
| **Statement** | — | Variante de Claim/Assertion | Eje Statement↔Claim | **Bajo** | Casi sinónimo de Claim; matiz "propuesto como verdadero" no siempre presente |
| **Claim** | — | Definido: propuesto, no establecido (Toulmin) | Claim por disciplina; eje Statement↔Claim | **Medio** | Coincidencia en "afirmación sujeta a respaldo" |
| **Fact** | Separación hecho↔interpretación | Definido: verificable; objeto del mundo vs afirmación verificada | Hecho por disciplina; ejes Evidence↔Fact y Fact↔Finding; umbral variable | **Medio** | El **umbral de "hecho"** diverge entre disciplinas |
| **Finding** | — | Definido: resultado de un análisis | Ejes Fact↔Finding y Finding↔Conclusion | **Bajo** | Intermedio vs conclusivo sin consenso |
| **Hypothesis** | Hipótesis derivadas de la evidencia | Definida: tentativa contrastable | Hipótesis por disciplina; **hipótesis competidoras** (ACH) | **Alto** | Coinciden: tentativa contrastable; valor del **descarte** de alternativas |
| **Conclusion** | — | Definida: afirmación final del razonamiento | Conclusión por disciplina; justificación; Finding↔Conclusion | **Medio** | Grado de finalidad/confianza variable |
| **Knowledge** | Enfoque knowledge-centric | Definido: DIKW; tácito/explícito | Eje Knowledge↔Belief; conocimiento justificado revisable | **Medio** | Frontera con información y con creencia |
| **Provenance** | **Procedencia de primera clase**, costosa de retrofitar | Definida: origen+historia; W3C PROV; cadena de custodia | Procedencia/justificación adjunta como **patrón común** | **Alto** | Concepto más transversal y mejor consensuado |
| **Metadata** | — | Definida: datos sobre datos; tipos | — (no aislado) | **1 fuente** | Tratada en profundidad solo en WP-0009 |
| **Trust** | Fiabilidad/credibilidad mencionadas | Bajo "Source" (fiabilidad), no como "Trust" | Fiabilidad de fuente vs credibilidad de información | **Bajo** | Aparece como **fiabilidad/credibilidad**, no como "Trust" nombrado |
| **Confidence** | — | No aislado | Eje Certainty↔Confidence; representación de incertidumbre (niveles) | **1 fuente** | Sustancialmente solo en WP-0010 (graduable) |
| **Justification** | Implícito (la evidencia sostiene afirmaciones) | No aislado | Eje Truth↔Justification; justificación de la conclusión por disciplina | **Medio** | Central en WP-0010; implícito en los otros |
| **Interpretation** | **Separación hecho↔interpretación** (inmutable vs mutable) | Ambigüedad dato↔interpretación (Annotation, Fact) | Separación hecho↔interpretación como patrón recurrente | **Alto** | Separación constatación/interpretación muy consensuada |
| **Entity** | Entidades del mundo ligadas a la evidencia (implícito) | Definida: cosa identificable; sentido PROV vs E-R | Entity/Relationship en Knowledge Representation | **Medio** | Sentido técnico variable (PROV vs E-R vs NLP) |
| **Event** | Cronologías (implícito) | Definido: suceso en tiempo/lugar; CIDOC CRM; Activity | Eventos en cronologías/forense | **Medio** | Granularidad (instante/intervalo) y hecho vs afirmación |
| **Relationship** | **Relaciones de primera clase** (corrobora/contradice) | Definida: enlace vs primera clase; predicado/tripleta | Relación/tripleta en KR; análisis de redes | **Medio** | Recurrente "corrobora/contradice"; enlace vs primera clase sin cerrar |
| **Case** | Enfoque case-centric | Definido: asunto; vs Investigation | Disciplina Criminal Investigation (contexto) | **Medio** | Solapamiento Case↔Investigation |
| **Investigation** | Implícito (contexto de investigación) | Definida: proceso de indagación; vs Case | Proceso de investigación (varias disciplinas) | **Bajo** | Proceso vs contenedor sin consenso |

### 4.2 Temas recurrentes adicionales (detectados en los tres)

| Tema | WP-0007 | WP-0009 | WP-0010 | Consenso | Observaciones |
|---|---|---|---|---|---|
| **Unidad mínima de evidencia / granularidad** | Riesgo de identidad/granularidad de la evidencia | "Evidence Item": unidad discreta; granularidad variable | Unidad mínima distinta por disciplina | **Medio** | Todos señalan el problema; **ninguno fija** la granularidad |
| **Evidencia como rol relacional** | Explícito | Implícito (material vs relación) | Explícito (rol respecto a hipótesis) | **Alto** | Patrón consistente en los tres |
| **Inmutabilidad + revisión (no monotonía)** | Hecho inmutable vs interpretación mutable | Inmutabilidad histórica + interpretación mutable | Conocimiento revisable; mecanismos de refutación | **Alto** | Conocimiento **provisional y revisable** consensuado |
| **Atribución (afirmación ligada a emisor)** | Implícito (procedencia) | Assertion atribuible (reificación) | Afirmaciones atribuibles a fuente/analista | **Medio** | Recurrente, con distinto grado de formalización |
| **Incertidumbre explícita y graduada** | — | Fiabilidad bajo Source | Representación de incertidumbre en todas las disciplinas | **Medio** | Fuerte en WP-0010; parcial en los otros |

---

## 5. Patrones recurrentes

> Agrupación de lo sintetizado. No se proponen soluciones.

### 5.1 Patrones ampliamente compartidos (consenso Alto en los tres)
- **Procedencia como concepto transversal y crítico** (Provenance).
- **Evidencia como rol relacional** (algo es evidencia *respecto a* una hipótesis), no como clase de objeto fija.
- **Separación hecho ↔ interpretación** (constatación inmutable vs valoración mutable).
- **Conocimiento provisional y revisable** (inmutabilidad del registro + revisión/refutación).
- **Hipótesis como tentativa contrastable**, con valor del **descarte de alternativas**.

### 5.2 Patrones frecuentes (consenso Medio)
- **Gradiente epistémico** observación → claim → hecho/finding → conclusión, con fronteras graduables.
- **El documento/fuente como portador**, no como verdad en sí.
- **Atribución** de las afirmaciones a un emisor/fuente.
- **Relaciones "corrobora/contradice"** entre piezas de conocimiento.
- **Justificación** como criterio que distingue conocimiento de mera creencia.

### 5.3 Conceptos controvertidos (tratamiento divergente)
- **Umbral de "Fact"** (cuándo una afirmación corroborada pasa a "hecho").
- **Relationship**: simple enlace vs entidad de primera clase.
- **Finding vs Conclusion**: grado de finalidad.
- **Case vs Investigation**: contenedor vs proceso.

### 5.4 Conceptos sin consenso / poco cubiertos
- **Trust** (aparece como fiabilidad/credibilidad, no nombrado como tal).
- **Confidence** (sustancialmente solo en WP-0010).
- **Metadata** (sustancialmente solo en WP-0009).
- **Information** y **Statement** (frontera difusa con Knowledge y Claim respectivamente).

### 5.5 Conceptos claramente dependientes de la disciplina
- **Fact**, **Conclusion**, **Evidence** (admisibilidad legal vs reproducibilidad científica vs verificación periodística vs aserción en KR).
- **Unidad mínima de conocimiento** (dato, item de información, artefacto, tripleta, argumento, elemento de prueba).
- **Representación de la incertidumbre** (cuantitativa vs escalas verbales vs estándares de prueba).

---

## 6. Divergencias observadas

1. **Umbral de "hecho"**: determinado por autoridad (legal), consenso reproducible (ciencia), verificación multifuente (periodismo) o suposición de la base de conocimiento (KR) — según WP-0009 y WP-0010.
2. **Naturaleza de Relationship**: WP-0007 la trata como de primera clase (corrobora/contradice); WP-0009 contrasta enlace vs primera clase; WP-0010 la ve como tripleta/arista.
3. **Cuantitativo vs cualitativo** en la incertidumbre (WP-0010), frente al tratamiento mínimo en WP-0007/WP-0009.
4. **Case vs Investigation**: distinción explícita en WP-0009; tratamiento contextual/implícito en WP-0007 y WP-0010.
5. **Cobertura desigual**: conceptos como Metadata, Trust o Confidence reciben tratamiento sustantivo en un solo WP.

> Estas divergencias se **registran**, no se resuelven (restricción del WP).

---

## 7. Vacíos de conocimiento

> Limitaciones de la evidencia disponible (qué **no** está bien cubierto por los tres WP). No es investigación nueva; es identificación de lagunas.

- **Information** y **Statement** carecen de tratamiento aislado y consistente (frontera difusa con Knowledge y Claim).
- **Trust** no se aborda como concepto propio; solo como fiabilidad/credibilidad de fuente/información.
- **Confidence** y **Metadata** se sustentan esencialmente en una sola fuente cada uno.
- **Granularidad/identidad de la unidad mínima de evidencia**: señalada como problema por los tres, pero **sin** análisis resolutivo en ninguno.
- **Relación formal entre conceptos** (p. ej. cómo se conectan Evidence, Claim, Fact, Finding, Conclusion entre sí): los WP los definen por separado pero **no** trazan sus interrelaciones (coherente con que eso correspondería al diseño, fuera de alcance).
- **Cuantificación de la certeza**: descrita a nivel de patrón (WP-0010) pero sin profundizar por concepto.

---

## 8. Observaciones

- La síntesis confirma, sin decidir nada, que los puntos de **mayor consenso** (procedencia, evidencia relacional, separación hecho↔interpretación, conocimiento revisable, hipótesis contrastable) son **candidatos consistentes** a ser considerados por el Principal Architect en ARCH-0002. La calificación "candidato" es **descriptiva**: no constituye una propuesta ni un principio.
- Los puntos de **menor consenso o cobertura** (umbral de hecho, Relationship, Case/Investigation, Trust, Confidence, Information/Statement) son los que probablemente requerirán **definición propia** (en línea con AC-0003, sin introducir aquí decisiones).
- Toda la matriz es **trazable** a los tres WP citados; no se ha incorporado conocimiento externo.

---

## 9. Referencias

> Únicamente los tres Work Packages de investigación. No se citan fuentes externas (las fuentes primarias residen dentro de cada WP).

- **WP-0007** — Evidence-Centric Domain Research · `docs/architecture/Evidence-Centric-Domain-Research.md`
- **WP-0009** — Domain Ontology Research · `docs/research/DOMAIN-ONTOLOGY-RESEARCH.md`
- **WP-0010** — Epistemic Domain Pattern Research · `docs/research/EPISTEMIC-DOMAIN-PATTERN-RESEARCH.md`

---

_Fin de la síntesis. No incorpora conocimiento ni fuentes nuevas, no resuelve contradicciones, no elige terminología, no prioriza disciplinas y no contiene decisiones de arquitectura. Documento de apoyo exclusivo para el Principal Architect en la redacción de ARCH-0002 — Domain Philosophy._
