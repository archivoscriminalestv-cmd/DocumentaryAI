# EPISTEMIC DOMAIN PATTERN RESEARCH — DocumentaryAI (WP-0010)

| Campo | Valor |
|---|---|
| **Document ID** | RES-EPISTEMIC-PATTERNS |
| **Title** | Epistemic Domain Pattern Research — DocumentaryAI |
| **Status** | Draft (research) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | `docs/research/DOMAIN-ONTOLOGY-RESEARCH.md`, `docs/architecture/Evidence-Centric-Domain-Research.md` |

> **Documento de investigación.** Evidencia para la redacción de **ARCH-0002 — Domain Philosophy**.
> **No** diseña la ontología de DocumentaryAI, **no** elige una disciplina de referencia, **no** propone modelo conceptual ni elementos DDD, **no** redacta RFC/ADR/ARCH/SPEC y **no** decide.
> Objetivo: **documentar patrones existentes** sobre cómo se construye conocimiento a partir de observación, evidencia y razonamiento. Cuando hay varias interpretaciones válidas, **se documentan todas**.

---

## 1. Objetivo

Investigar cómo distintas disciplinas modelan el **ciclo de construcción del conocimiento** —de la observación y la evidencia al razonamiento y la conclusión— para ofrecer al Principal Architect un repertorio de **patrones conceptuales** comparados.

El documento es **descriptivo**: no propone un modelo para DocumentaryAI ni prioriza ninguna disciplina. Las hipótesis arquitectónicas mencionadas en el contexto del WP (la evidencia como rol contextual, el sistema como modelador de "conocimiento justificable", etc.) se tratan como **hipótesis abiertas del Principal Architect**, no como premisas de esta investigación.

---

## 2. Metodología

- **Disciplinas analizadas (9):** Scientific Method, Intelligence Cycle, Criminal Investigation, Investigative Journalism, Digital Forensics, Knowledge Representation, Argumentation Theory, Evidence-Based Medicine, Legal Evidence.
- **Rejilla por disciplina (9 aspectos):** (1) unidad mínima de conocimiento, (2) qué es una observación, (3) qué es evidencia, (4) qué es un hecho, (5) qué es una afirmación, (6) qué es una hipótesis, (7) cómo se justifica una conclusión, (8) cómo se representa la incertidumbre, (9) cómo se gestiona la revisión/refutación.
- **Comparativa transversal:** ocho ejes de contraste (Observation vs Evidence; Evidence vs Fact; Fact vs Finding; Finding vs Conclusion; Statement vs Claim; Knowledge vs Belief; Certainty vs Confidence; Truth vs Justification).
- **Fuentes:** obras y estándares canónicos por disciplina (ver §9), citados por nombre para verificación; no se reproduce su contenido ni se inventan citas literales.
- **Neutralidad:** descripción sin selección. Ninguna disciplina se presenta como modelo a seguir.

---

## 3. Patrones por disciplina

### 3.1 Scientific Method
- **Unidad mínima de conocimiento:** la proposición empírica contrastable (hipótesis falsable y sus datos).
- **Observación:** dato registrado mediante medición o percepción controlada y, idealmente, reproducible.
- **Evidencia:** observaciones/datos que confirman o desmienten una hipótesis; su fuerza es el "peso de la evidencia".
- **Hecho:** afirmación establecida por evidencia y consenso reproducible; revisable en principio.
- **Afirmación (claim):** enunciado propuesto a contraste; aún no establecido.
- **Hipótesis:** conjetura falsable que predice observaciones.
- **Justificación de la conclusión:** inferencia (deductiva/inductiva/abductiva) desde los datos, sometida a revisión por pares y replicación.
- **Incertidumbre:** estadística (p-valores, intervalos de confianza, tamaños de efecto, barras de error).
- **Revisión/refutación:** falsación, replicación fallida, corrección y retractación; el conocimiento es provisional.

### 3.2 Intelligence Cycle
- **Unidad mínima de conocimiento:** el "item of information" (reporte) valorado, que se integra en un juicio analítico.
- **Observación:** información recogida por una fuente (humana, técnica, abierta).
- **Evidencia:** información valorada que apoya/contradice una hipótesis; se separa fiabilidad de fuente de credibilidad de la información.
- **Hecho:** raramente "hecho" absoluto; se habla de información corroborada con alta confianza.
- **Afirmación:** juicio o estimación analítica atribuida a un analista.
- **Hipótesis:** explicación competidora evaluada frente a la evidencia (Analysis of Competing Hypotheses).
- **Justificación de la conclusión:** ponderación de hipótesis por consistencia con la evidencia; énfasis en evidencia diagnóstica (la que discrimina entre hipótesis).
- **Incertidumbre:** "words of estimative probability" y niveles de confianza explícitos (escalas tipo Almirantazgo/NATO).
- **Revisión/refutación:** reevaluación continua al llegar nueva información; las estimaciones se actualizan.

### 3.3 Criminal Investigation
- **Unidad mínima de conocimiento:** el indicio/dato del caso vinculado a una línea de investigación.
- **Observación:** constatación en la escena o en diligencias (lo percibido/recogido).
- **Evidencia:** material o testimonio que sostiene/descarta una hipótesis sobre autoría, medios o secuencia (principio de intercambio de Locard).
- **Hecho:** circunstancia tenida por acreditada dentro del caso.
- **Afirmación:** declaración (de testigo, sospechoso, perito) a corroborar.
- **Hipótesis:** teoría del caso / línea de investigación (móvil, oportunidad, medios).
- **Justificación de la conclusión:** convergencia de indicios y descarte de alternativas; cadena de custodia para sostener la integridad.
- **Incertidumbre:** fuerza del caso, corroboración múltiple; lenguaje cualitativo de probabilidad.
- **Revisión/refutación:** reapertura ante nueva evidencia; exoneraciones; descarte de líneas.

### 3.4 Investigative Journalism
- **Unidad mínima de conocimiento:** la afirmación verificable atribuida a fuentes.
- **Observación:** lo presenciado/documentado por el periodista o reportado por una fuente.
- **Evidencia:** documentos, registros, testimonios que respaldan una afirmación; preferencia por la corroboración independiente.
- **Hecho:** afirmación verificada por múltiples fuentes/documentos (estándar editorial).
- **Afirmación (claim):** lo que una fuente sostiene; objeto de verificación.
- **Hipótesis:** línea de investigación periodística a confirmar o desmentir.
- **Justificación de la conclusión:** verificación cruzada, regla de las múltiples fuentes, derecho de réplica, transparencia de procedencia.
- **Incertidumbre:** grado de atribución (on/off the record), número y calidad de fuentes; cautela editorial.
- **Revisión/refutación:** correcciones y retractaciones públicas; actualización tras nuevos datos.

### 3.5 Digital Forensics
- **Unidad mínima de conocimiento:** el artefacto/evidencia digital identificable con su procedencia técnica.
- **Observación:** lo recuperado/observado mediante procedimientos forenses (con integridad verificada).
- **Evidencia:** artefactos admisibles que sostienen una hipótesis sobre lo ocurrido; integridad por hash y cadena de custodia.
- **Hecho:** estado técnico verificable y reproducible a partir del artefacto.
- **Afirmación:** interpretación pericial sobre lo que el artefacto indica.
- **Hipótesis:** explicación del incidente/secuencia de eventos.
- **Justificación de la conclusión:** reproducibilidad del análisis, métodos validados, documentación de procedimiento; razón de verosimilitud (likelihood ratio) en informes periciales.
- **Incertidumbre:** tasas de error de métodos, likelihood ratios, límites de la herramienta.
- **Revisión/refutación:** reanálisis independiente, validación de herramientas, contraperitaje.

### 3.6 Knowledge Representation
- **Unidad mínima de conocimiento:** la aserción/tripleta (sujeto-predicado-objeto) en un grafo u ontología.
- **Observación:** dato de entrada antes de su formalización como aserción.
- **Evidencia:** en sistemas con soporte, la justificación o procedencia adjunta a una aserción.
- **Hecho:** aserción asumida como verdadera en la base de conocimiento (con suposición de mundo abierto o cerrado, según el sistema).
- **Afirmación:** la tripleta afirmada, posiblemente atribuida a un emisor (reificación).
- **Hipótesis:** aserción tentativa o conocimiento por defecto sujeto a revisión.
- **Justificación de la conclusión:** inferencia lógica (lógica descriptiva), razonamiento probabilístico (redes bayesianas) o por defecto (no monótono).
- **Incertidumbre:** probabilidades, lógica difusa, factores de certeza, pesos en aristas.
- **Revisión/refutación:** razonamiento no monótono, revisión de creencias (teoría AGM), sistemas de mantenimiento de la verdad (TMS).

### 3.7 Argumentation Theory
- **Unidad mínima de conocimiento:** el argumento (afirmación + apoyo) o, en modelos abstractos, el "argumento" como nodo con relaciones de ataque.
- **Observación:** dato/grounds que sirve de base a una afirmación.
- **Evidencia:** los "grounds/data" que respaldan un "claim" (modelo de Toulmin), conectados por una "warrant".
- **Hecho:** afirmación aceptada (no atacada con éxito) en el marco del debate.
- **Afirmación (claim):** la tesis que el argumento defiende.
- **Hipótesis:** afirmación defendible sujeta a refutación.
- **Justificación de la conclusión:** estructura claim–grounds–warrant–backing–qualifier–rebuttal; aceptabilidad según relaciones de ataque/defensa (argumentación abstracta de Dung).
- **Incertidumbre:** "qualifiers" (p. ej. "presumiblemente"), razonamiento derrotable (defeasible).
- **Revisión/refutación:** un argumento puede ser **rebatido** (rebuttal), **socavado** (undercut) o derrotado por otro; la aceptabilidad se recalcula.

### 3.8 Evidence-Based Medicine
- **Unidad mínima de conocimiento:** la respuesta a una pregunta clínica estructurada (p. ej. formato PICO) sustentada en estudios.
- **Observación:** dato clínico o resultado de estudio.
- **Evidencia:** cuerpo de estudios jerarquizado por diseño y calidad (jerarquía de la evidencia; revisiones sistemáticas en la cúspide).
- **Hecho:** efecto/asociación respaldado por evidencia de alta calidad y consistente.
- **Afirmación:** recomendación o estimación de efecto.
- **Hipótesis:** pregunta de investigación a contrastar.
- **Justificación de la conclusión:** síntesis de evidencia (meta-análisis), valoración de la **certeza** del cuerpo de evidencia (p. ej. GRADE), fuerza de la recomendación.
- **Incertidumbre:** intervalos de confianza, niveles de certeza GRADE, NNT, sesgo y heterogeneidad.
- **Revisión/refutación:** actualización de revisiones sistemáticas y guías ("living guidelines") al aparecer nueva evidencia.

### 3.9 Legal Evidence
- **Unidad mínima de conocimiento:** el elemento de prueba (exhibit/testimonio) relevante para un hecho en disputa.
- **Observación:** lo percibido por un testigo o recogido como prueba.
- **Evidencia:** prueba admisible (relevante, fiable, no excluida) que tiende a probar/refutar un hecho.
- **Hecho:** cuestión de hecho determinada por el juzgador ("trier of fact"), separada de la cuestión de derecho.
- **Afirmación:** alegación de parte (pendiente de prueba).
- **Hipótesis:** la teoría del caso de cada parte.
- **Justificación de la conclusión:** valoración conforme a un **estándar de prueba** (preponderancia / clara y convincente / más allá de toda duda razonable); análisis de la masa probatoria (gráficos de Wigmore; enfoques bayesianos o de "plausibilidad relativa").
- **Incertidumbre:** estándares de prueba escalonados; likelihood ratios en prueba pericial.
- **Revisión/refutación:** recursos/apelación, prueba nueva, revisión de condenas, exclusión de prueba.

---

## 4. Comparativa transversal

> Contraste descriptivo de ocho ejes. No se zanja ninguno; se muestran las posturas.

| Eje | Patrón común | Divergencias relevantes |
|---|---|---|
| **Observation vs Evidence** | La observación es la constatación; se vuelve "evidencia" solo **en relación con** una hipótesis a la que apoya/refuta. | Forense/legal exigen procedimiento e integridad para que la observación "cuente"; ciencia exige reproducibilidad; en KR la frontera es la formalización como aserción justificada. |
| **Evidence vs Fact** | La evidencia *sostiene*; el hecho es lo que se *tiene por establecido* tras suficiente evidencia. | El umbral varía: "hecho" jurídico (decidido por el juzgador) ≠ "hecho" científico (consenso reproducible) ≠ "hecho" periodístico (verificado por múltiples fuentes). |
| **Fact vs Finding** | El hecho es un estado tenido por cierto; el *finding* es el resultado de un análisis. | Auditoría/forense/inteligencia usan "finding" como hallazgo con soporte (a veces interpretativo); en ciencia el "resultado" puede ser un hecho nuevo. |
| **Finding vs Conclusion** | El *finding* alimenta la conclusión; la conclusión es el juicio final del razonamiento. | El grado de finalidad difiere: conclusión jurídica (vinculante) ≠ conclusión científica (provisional) ≠ juicio de inteligencia (con confianza explícita). |
| **Statement vs Claim** | Todo *claim* es un *statement*; el *claim* añade el matiz de "propuesto como verdadero, sujeto a respaldo". | Argumentación y fact-checking marcan fuerte el "claim"; en KR un "statement/assertion" puede no llevar carga de disputa. |
| **Knowledge vs Belief** | El conocimiento se distingue de la mera creencia por la **justificación** (y, clásicamente, la verdad). | Epistemología discute la verdad como requisito; KR e inteligencia operan con "conocimiento" justificado pero revisable (más cercano a creencia justificada). |
| **Certainty vs Confidence** | La certeza es estado (cualitativo, casi binario); la confianza es **graduable** y expresable. | Ciencia/EBM/forense usan medidas cuantitativas (CI, GRADE, likelihood ratios); inteligencia usa escalas verbales calibradas; derecho usa estándares escalonados. |
| **Truth vs Justification** | Casi todas las disciplinas operan sobre **justificación** alcanzable, no sobre verdad absoluta. | Lógica/matemática hablan de verdad/prueba; el resto persigue justificación suficiente para el contexto (admisibilidad, replicabilidad, corroboración, estándar de prueba). |

---

## 5. Conceptos comunes (patrones recurrentes)

1. **Gradiente epistémico, no categorías tajantes:** todas las disciplinas describen un recorrido observación → evidencia → afirmación → hecho/finding → conclusión, con **fronteras graduables** por nivel de respaldo.
2. **La evidencia es relacional:** en casi todas, "evidencia" no es una clase de objeto sino un **rol** que algo adquiere respecto a una hipótesis (coherente con la hipótesis del contexto del WP, aquí solo constatada, no adoptada).
3. **Procedencia/justificación adjunta:** el valor de una afirmación depende de **de dónde viene** y **cómo se sostiene** (custodia, fuente, método, cita).
4. **Hipótesis competidoras y descarte:** el razonamiento avanza tanto confirmando como **eliminando alternativas** (ACH, teoría del caso, diagnóstico diferencial, refutación).
5. **Incertidumbre explícita y graduada:** todas representan el "cuánto lo sabemos", con escalas cuantitativas o verbales calibradas.
6. **Conocimiento revisable (no monotonía):** todas prevén **revisar o refutar** lo establecido ante nueva evidencia (replicación, reevaluación, corrección, apelación, belief revision).
7. **Separación hecho ↔ interpretación:** recurrente distinción entre lo constatado y lo inferido/valorado (reafirma WP-0007).
8. **Atribución:** las afirmaciones suelen ir **ligadas a un emisor/analista/fuente**, no flotar de forma anónima.

---

## 6. Divergencias

1. **Umbral de "hecho":** decidido por una autoridad (derecho), por consenso reproducible (ciencia), por verificación multifuente (periodismo) o por suposición de la base de conocimiento (KR).
2. **Cuantitativo vs cualitativo en la incertidumbre:** estadística/likelihood ratios/GRADE frente a escalas verbales de inteligencia o estándares jurídicos.
3. **Unidad mínima:** dato/medición (ciencia), item de información (inteligencia), artefacto (forense), tripleta (KR), argumento (argumentación), elemento de prueba (derecho), afirmación atribuida (periodismo).
4. **Papel de la procedencia:** crítica y formal en forense/legal/archivo; importante pero menos formal en periodismo; opcional/variable en KR.
5. **Mecanismo de revisión:** falsación/replicación (ciencia), actualización analítica (inteligencia), apelación/prueba nueva (derecho), corrección pública (periodismo), revisión de creencias formal (KR), defeat/undercut (argumentación), actualización de revisiones (EBM).
6. **Verdad vs aceptabilidad:** lógica/matemática persiguen verdad/prueba; el resto, una **aceptabilidad contextual** (admisibilidad, consenso, corroboración).
7. **Tratamiento de hipótesis competidoras:** central y explícito en inteligencia y medicina (diagnóstico diferencial); más implícito en otras.

---

## 7. Observaciones

- El patrón más estable entre disciplinas es el **gradiente justificacional** y la **naturaleza relacional de la evidencia**; el más divergente, el **umbral de "hecho"** y la **forma de expresar incertidumbre**.
- La mayoría de disciplinas operan sobre **justificación revisable**, no sobre verdad absoluta: el conocimiento es **provisional y atribuible**.
- Estos hallazgos **describen** opciones; no implican que DocumentaryAI deba adoptar ninguna. Las hipótesis arquitectónicas del contexto siguen siendo del Principal Architect.
- Conexión con conclusiones previas: refuerzan AC-0001 (no hay terminología universal) y AC-0003 (necesidad de un lenguaje ubicuo propio), sin introducir decisiones nuevas.

---

## 8. Preguntas abiertas para el Principal Architect

1. ¿Modelará DocumentaryAI la evidencia como **rol contextual** (algo es evidencia *respecto a* una hipótesis) o como objeto fundamental?
2. ¿Qué **gradiente epistémico** propio adoptará (qué pasos distinguirá entre observación y conclusión y con qué nombres)?
3. ¿Cómo se representará la **incertidumbre**: cuantitativa, escalas verbales calibradas, estándares escalonados, o combinación?
4. ¿Qué **umbral** definirá "hecho" frente a afirmación corroborada, y quién/qué lo determina?
5. ¿El sistema tratará las afirmaciones como **atribuibles a una fuente/analista** por defecto?
6. ¿Se modelará el **descarte de hipótesis competidoras** como parte del razonamiento, o solo el apoyo positivo?
7. ¿Cómo se gestionará la **revisión/refutación** del conocimiento (versionado, no monotonía, correcciones, trazas de cambio)?
8. ¿El objetivo es representar **conocimiento justificable** (justificación + procedencia) más que documentos, y con qué implicaciones para la unidad mínima?
9. ¿Se mantendrá explícita la **separación hecho ↔ interpretación** en el propio modelo?

---

## 9. Referencias

> Fuentes canónicas por disciplina, citadas por su nombre reconocido para verificación por el Principal Architect.

- **Scientific Method:** K. Popper, *The Logic of Scientific Discovery* (falsabilidad); C. Hempel (modelo nomológico-deductivo); literatura estándar sobre inferencia inductiva/abductiva y estadística inferencial.
- **Intelligence Cycle:** R. J. Heuer Jr., *Psychology of Intelligence Analysis* y *Analysis of Competing Hypotheses (ACH)*; *Words of Estimative Probability* (S. Kent); *Admiralty/NATO System* de fiabilidad/credibilidad.
- **Criminal Investigation:** principio de intercambio de *Locard*; Inman & Rudin, *Principles and Practice of Criminalistics*; manuales de gestión de investigación criminal (p. ej. doctrina tipo ACPO).
- **Investigative Journalism:** *The Verification Handbook*; estándares de *fact-checking* y de corroboración multifuente.
- **Digital Forensics:** *NIST SP 800-86*; E. Casey, *Digital Evidence and Computer Crime*; uso de *likelihood ratios* en informe pericial.
- **Knowledge Representation:** *RDF/OWL* y lógica descriptiva; redes bayesianas (J. Pearl); razonamiento no monótono; teoría de revisión de creencias *AGM* (Alchourrón-Gärdenfors-Makinson); *Truth Maintenance Systems* (Doyle).
- **Argumentation Theory:** S. Toulmin, *The Uses of Argument*; D. Walton (esquemas de argumentación); P. M. Dung (argumentación abstracta); razonamiento *defeasible*.
- **Evidence-Based Medicine:** D. Sackett et al., *Evidence-Based Medicine*; sistema *GRADE*; *Cochrane Handbook*; jerarquía de la evidencia; marco *PICO*.
- **Legal Evidence:** J. H. Wigmore (*Wigmore charts*); estándares de prueba (preponderance / clear and convincing / beyond reasonable doubt); enfoques bayesianos y de *relative plausibility* (Allen & Pardo); reglas de evidencia (p. ej. *Federal Rules of Evidence*).
- **Transversal (conocimiento):** jerarquía *DIKW*; debate epistemológico sobre *creencia verdadera justificada* (Gettier y posteriores).

---

_Fin de la investigación. Documento completamente descriptivo: no diseña la ontología de DocumentaryAI, no elige disciplina de referencia, no propone modelo ni arquitectura, no contiene decisiones. Su único fin es servir de evidencia para ARCH-0002 — Domain Philosophy._
