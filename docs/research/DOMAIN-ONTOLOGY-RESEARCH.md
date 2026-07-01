# DOMAIN ONTOLOGY RESEARCH — DocumentaryAI (WP-0009)

| Campo | Valor |
|---|---|
| **Document ID** | RES-DOMAIN-ONTOLOGY |
| **Title** | Domain Ontology Research — DocumentaryAI |
| **Status** | Approved |
| **Architectural Review** | Approved by Principal Architect |
| **Decision Date** | 2026-06-28 |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | `docs/architecture/Evidence-Centric-Domain-Research.md`, `docs/architecture/RFC-0001-Architecture.md` |

> **Documento de investigación.** Base documental para el Sprint A-01 (Domain Discovery), previa a **ARCH-0002 — Domain Philosophy** y **RFC-0002 — Domain Model**.
> **No** diseña arquitectura, **no** modela DDD (Bounded Contexts, Aggregates, Value Objects, entidades, invariantes, reglas, relaciones definitivas), **no** propone implementación y **no** decide.
> Cuando existen varias interpretaciones válidas, **se documentan todas** sin seleccionar una.

---

## 1. Objetivo

Recopilar, de forma objetiva y referenciada, la **terminología y las definiciones** que las disciplinas relevantes emplean para los conceptos del dominio de DocumentaryAI (investigación de casos reales basada en evidencia). El fin es dar al Principal Architect un **mapa conceptual común** —con definiciones, usos, variantes, ambigüedades y diferencias entre disciplinas— sobre el que pueda fundamentar el diseño posterior del dominio.

Este documento **no** establece el vocabulario oficial del proyecto: lo prepara.

---

## 2. Metodología

- **Disciplinas consultadas** (marco de referencia): Digital Forensics, Intelligence Analysis, Investigative Journalism, Scientific Research, Evidence Management, Knowledge Graphs, Provenance Models, Records & Archives Management.
- **Enfoque:** para cada concepto se recoge (a) **Definición** sintetizada, (b) **Contextos de uso**, (c) **Variantes terminológicas**, (d) **Ambigüedades**, (e) **Diferencias entre disciplinas**.
- **Fuentes:** estándares y obras canónicas de cada disciplina (ver §10). Las referencias se citan por su nombre reconocido para que el Principal Architect pueda verificarlas; este documento no reproduce su contenido literal ni inventa citas concretas.
- **Neutralidad:** ante interpretaciones divergentes, se listan todas. No se prioriza ninguna ni se "traduce" al dominio de DocumentaryAI.
- **Límites:** sin modelado, sin decisiones, sin propuestas. Es un trabajo de *vocabulario*, no de *diseño*.

---

## 3. Inventario de conceptos

Agrupación instrumental (solo para lectura; **no** implica relaciones ni jerarquía de dominio):

- **A. Fuentes y materiales:** Document · Source · Collection · Metadata · Provenance · Citation · Reference · Annotation
- **B. Unidades epistémicas (evidencia y aserción):** Evidence · Evidence Item · Observation · Fact · Claim · Assertion · Finding · Hypothesis · Conclusion
- **C. Modelo del mundo:** Entity · Actor · Event · Relationship
- **D. Contenedores de investigación:** Case · Investigation
- **E. Conocimiento:** Knowledge

Total: 24 conceptos.

---

## 4. Definiciones recopiladas

> Para cada concepto: Definición · Contextos de uso · Variantes terminológicas · Ambigüedades · Diferencias entre disciplinas.

### A. Fuentes y materiales

#### Document
- **Definición:** Unidad de contenido registrada en un soporte (texto, imagen, audio, vídeo, expediente), tratada como objeto identificable.
- **Contextos de uso:** Archivística y records management (objeto a preservar); forense (artefacto digital); periodismo (material de partida); e-discovery (unidad de revisión).
- **Variantes:** "record", "file", "artifact", "item", "asset", "exhibit", "manifestation/item" (FRBR/IFLA-LRM).
- **Ambigüedades:** ¿es el *contenedor* o su *contenido*? ¿un PDF es un documento, o lo son también cada página/anexo? Relación con "versión".
- **Diferencias entre disciplinas:** Archivística distingue documento de "record" (con valor probatorio/oficial); forense lo ve como artefacto con metadatos técnicos; bibliografía (FRBR) lo descompone en Work/Expression/Manifestation/Item.

#### Source
- **Definición:** Origen del que procede la información o el material: persona, organización, publicación, sistema o documento del que se obtiene algo.
- **Contextos de uso:** Inteligencia (fuente humana/técnica, con fiabilidad); periodismo (fuente atribuible/anónima); ciencia (fuente primaria/secundaria); provenance (agente/origen).
- **Variantes:** "origin", "informant", "provider", "primary/secondary/tertiary source", "feed".
- **Ambigüedades:** "source" puede ser el *documento* o el *autor del documento*; confusión frecuente entre fuente y evidencia que aporta.
- **Diferencias entre disciplinas:** Inteligencia gradúa la *fiabilidad de la fuente* separada de la *credibilidad de la información* (sistema Almirantazgo/NATO); ciencia clasifica por primario/secundario; periodismo por grado de atribución (on/off the record).

#### Collection
- **Definición:** Conjunto organizado de documentos/materiales agrupados por un criterio (procedencia, caso, tema).
- **Contextos de uso:** Archivística ("fonds"/colección/serie); e-discovery (corpus recopilado); museología (acervo).
- **Variantes:** "corpus", "dataset", "fonds", "series", "holdings", "batch".
- **Ambigüedades:** ¿es una agrupación física, lógica o por procedencia? Solapa con "Case" cuando el criterio es la investigación.
- **Diferencias entre disciplinas:** Archivística enfatiza el *principio de procedencia* y el orden original; ciencia/IA usan "dataset/corpus" sin esa carga.

#### Metadata
- **Definición:** Datos que describen otros datos: características, contexto, estructura o gestión de un recurso.
- **Contextos de uso:** Archivística y bibliografía (descripción); forense (metadatos técnicos: timestamps, hashes); web semántica.
- **Variantes:** descriptiva / estructural / administrativa / de preservación; "tags", "properties", "attributes".
- **Ambigüedades:** frontera con "datos" (lo que es metadato en un contexto es dato en otro); solapa con "provenance".
- **Diferencias entre disciplinas:** Dublin Core/archivística la estandarizan por tipos; forense prioriza metadatos probatorios e íntegros; KG la expresa como propiedades de nodos.

#### Provenance
- **Definición:** Registro del origen e historia de algo: de dónde viene, quién/qué lo produjo o modificó, y mediante qué proceso.
- **Contextos de uso:** Modelos de procedencia (W3C PROV); archivística (cadena de custodia documental); ciencia de datos (linaje); arte (pedigrí).
- **Variantes:** "lineage", "chain of custody", "pedigree", "audit trail", "derivation history".
- **Ambigüedades:** ¿solo el origen, o toda la historia de transformaciones? Relación con "metadata" (procedencia como subconjunto o como dimensión propia).
- **Diferencias entre disciplinas:** W3C PROV la formaliza (Entity/Activity/Agent); forense la liga a la cadena de custodia legal; ciencia de datos al *data lineage*.

#### Citation
- **Definición:** Indicación formal de la fuente de la que se toma una afirmación o material, normalmente con localización precisa.
- **Contextos de uso:** Investigación científica y académica; periodismo (atribución); derecho (referencia a prueba/jurisprudencia).
- **Variantes:** "reference" (a veces sinónimo), "attribution", "footnote", "pinpoint cite".
- **Ambigüedades:** "citation" vs "reference": en algunos estilos la cita es la marca en el texto y la referencia es la entrada completa; en otros se usan indistintamente.
- **Diferencias entre disciplinas:** Academia define formatos rígidos; periodismo prioriza la atribución a la fuente; derecho la localización exacta (pinpoint).

#### Reference
- **Definición:** Apuntador a un recurso o a otra pieza de información; entrada que permite localizar una fuente.
- **Contextos de uso:** Bibliografía (lista de referencias); informática (puntero/enlace); KG (vínculo).
- **Variantes:** "link", "pointer", "bibliographic entry", "cross-reference".
- **Ambigüedades:** se confunde con "citation" (ver arriba) y con "relationship/link" en grafos.
- **Diferencias entre disciplinas:** Academia: entrada bibliográfica; informática/KG: puntero navegable; archivística: referencia cruzada entre expedientes.

#### Annotation
- **Definición:** Información añadida por un analista sobre un material o fragmento: comentario, etiqueta, marca, interpretación.
- **Contextos de uso:** Anotación académica y NLP (corpus anotado); revisión documental; humanidades digitales.
- **Variantes:** "note", "tag", "label", "markup", "commentary", "highlight".
- **Ambigüedades:** ¿es metadato, interpretación o evidencia derivada? Mezcla de capa observacional y capa interpretativa.
- **Diferencias entre disciplinas:** NLP la trata como etiqueta estructurada (gold standard); humanidades como glosa interpretativa; revisión legal como marca de relevancia/privilegio.

### B. Unidades epistémicas

#### Evidence
- **Definición:** Información o material que tiende a apoyar o refutar una afirmación o hipótesis.
- **Contextos de uso:** Derecho/forense (prueba admisible); ciencia (datos que respaldan una hipótesis); inteligencia (información valorada).
- **Variantes:** "proof" (más fuerte, conclusivo), "exhibit", "supporting data", "indicator".
- **Ambigüedades:** evidencia ¿es el material en sí, o la *relación de apoyo* entre material y afirmación? "evidence" (incontable) vs "a piece of evidence".
- **Diferencias entre disciplinas:** Derecho exige admisibilidad/cadena de custodia; ciencia habla de *peso de la evidencia*; inteligencia separa información de su credibilidad; "proof" es casi exclusivo de matemática/lógica y derecho.

#### Evidence Item
- **Definición:** Una unidad discreta e identificable de evidencia (un elemento concreto dentro del conjunto de evidencia).
- **Contextos de uso:** Forense y gestión de evidencias (numeración de exhibits); e-discovery (item revisable).
- **Variantes:** "exhibit", "artifact", "piece of evidence", "evidence unit", "item".
- **Ambigüedades:** granularidad: ¿una frase, un documento, un objeto? Frontera con "Document" y con "Observation".
- **Diferencias entre disciplinas:** Forense lo formaliza con identificadores y custodia; ciencia rara vez "itemiza" así; inteligencia habla de "reporting"/"item of information".

#### Observation
- **Definición:** Constatación directa de un hecho o estado tal como es percibido o medido, antes de interpretarlo.
- **Contextos de uso:** Método científico (dato observado); inteligencia (observación de campo); forense (hallazgo observado en la escena).
- **Variantes:** "measurement", "reading", "datum", "sighting", "record of observation".
- **Ambigüedades:** ¿"observación" es neutra o ya teñida de interpretación? Solapa con "Fact" y con "Evidence Item".
- **Diferencias entre disciplinas:** Ciencia la distingue de la inferencia; inteligencia la asocia a un observador con fiabilidad; forense la liga al procedimiento de recogida.

#### Fact
- **Definición:** Afirmación que se considera verdadera y verificable; estado de cosas tenido por cierto.
- **Contextos de uso:** Periodismo/fact-checking (hecho verificado); derecho (hechos probados vs derecho); ciencia (hecho establecido).
- **Variantes:** "established fact", "ground truth", "verified statement", "matter of fact".
- **Ambigüedades:** ¿"hecho" objetivo del mundo o "afirmación verificada"? El grado de certeza para llamarlo "hecho" varía; frontera con "Claim corroborado".
- **Diferencias entre disciplinas:** Derecho separa *cuestiones de hecho* de *cuestiones de derecho*; periodismo lo define por verificación; ciencia por reproducibilidad/consenso.

#### Claim
- **Definición:** Afirmación propuesta como verdadera pero **aún no establecida**, sujeta a respaldo o refutación.
- **Contextos de uso:** Teoría de la argumentación (Toulmin: claim sostenido por grounds/warrant); fact-checking (afirmación a verificar); ciencia (afirmación a contrastar).
- **Variantes:** "assertion", "allegation" (con connotación legal/no probada), "statement", "proposition".
- **Ambigüedades:** "claim" vs "assertion" vs "statement" se usan casi como sinónimos; el matiz "no probado todavía" no siempre está presente.
- **Diferencias entre disciplinas:** Argumentación lo formaliza (modelo de Toulmin); derecho usa "allegation"; ciencia "hypothesis/claim"; periodismo "claim" como objeto de verificación.

#### Assertion
- **Definición:** Acto de afirmar algo como verdadero; la proposición afirmada por un emisor.
- **Contextos de uso:** Lógica y web semántica (una tripleta afirmada en un grafo); lingüística (acto de habla asertivo); seguridad (assertion de identidad).
- **Variantes:** "statement", "claim", "proposition", "triple" (en RDF).
- **Ambigüedades:** énfasis en el *acto* de afirmar vs la *proposición*; casi intercambiable con "claim" salvo el matiz de "quién lo afirma".
- **Diferencias entre disciplinas:** Web semántica/KG: una afirmación es una tripleta atribuible; argumentación/periodismo lo asimilan a "claim".

#### Finding
- **Definición:** Resultado de un análisis o investigación: algo que se ha determinado tras examinar la evidencia.
- **Contextos de uso:** Auditoría y forense (findings de un informe); ciencia (resultados); inteligencia (key findings).
- **Variantes:** "result", "determination", "outcome", "key finding", "result of analysis".
- **Ambigüedades:** ¿"finding" es intermedio (hallazgo) o ya conclusivo? Frontera con "Conclusion" y con "Fact establecido".
- **Diferencias entre disciplinas:** Auditoría/forense lo usan como hallazgo formal con soporte; ciencia como resultado; inteligencia como conclusión analítica con nivel de confianza.

#### Hypothesis
- **Definición:** Explicación o afirmación tentativa propuesta para ser contrastada con evidencia.
- **Contextos de uso:** Método científico; análisis de inteligencia (ACH — Analysis of Competing Hypotheses); investigación criminal (líneas de hipótesis).
- **Variantes:** "conjecture", "theory" (uso laxo), "working hypothesis", "lead/línea de investigación".
- **Ambigüedades:** "hypothesis" vs "theory" (en ciencia "theory" es más robusta; en habla común, lo contrario); grado de formalización.
- **Diferencias entre disciplinas:** Ciencia: falsable y contrastable; inteligencia: hipótesis competidoras evaluadas frente a evidencia (ACH); investigación criminal: hipótesis sobre autoría/secuencia.

#### Conclusion
- **Definición:** Afirmación final derivada del razonamiento sobre la evidencia y los hallazgos.
- **Contextos de uso:** Ciencia (conclusiones); derecho (veredicto/holding); inteligencia (juicio analítico con confianza); argumentación (conclusión inferida de premisas).
- **Variantes:** "determination", "verdict", "judgment", "inference", "ruling".
- **Ambigüedades:** frontera con "Finding"; grado de certeza; ¿provisional o definitiva?
- **Diferencias entre disciplinas:** Lógica: se sigue de premisas; derecho: decisión vinculante; inteligencia: juicio con probabilidad/confianza explícita; ciencia: sujeta a revisión.

### C. Modelo del mundo

#### Entity
- **Definición:** Cualquier "cosa" identificable y distinguible del mundo o del modelo: persona, lugar, objeto, organización, concepto.
- **Contextos de uso:** Modelado de datos (entidad-relación); KG/web semántica (nodo); NLP (Named Entity Recognition); provenance (PROV Entity).
- **Variantes:** "object", "node", "thing", "named entity", "resource".
- **Ambigüedades:** "entity" abarca desde objetos físicos a conceptos abstractos; en PROV "Entity" tiene un sentido específico (algo con procedencia) distinto del de E-R.
- **Diferencias entre disciplinas:** E-R: tipo con atributos; KG: nodo con URI; NLP: mención de entidad en texto; PROV: objeto con linaje.

#### Actor
- **Definición:** Entidad capaz de actuar o participar: persona u organización que realiza o sufre una acción.
- **Contextos de uso:** Inteligencia/criminología (actores, personas de interés); UML/casos de uso (actor); provenance (Agent); narrativa (personaje/agente).
- **Variantes:** "agent", "party", "person of interest", "stakeholder", "participant".
- **Ambigüedades:** ¿"actor" = persona, o cualquier agente (incluido un sistema u organización)? Solapa con "Entity" y con "Agent (PROV)".
- **Diferencias entre disciplinas:** PROV usa "Agent"; UML "Actor" (rol externo); criminología "persona de interés/sospechoso"; sociología "actor social".

#### Event
- **Definición:** Suceso que ocurre en un tiempo (y normalmente lugar), con participantes; cambio de estado del mundo.
- **Contextos de uso:** Cronologías/historiografía; CIDOC CRM (eventos como núcleo); KG (eventos como nodos); forense (timeline de incidentes); narrativa.
- **Variantes:** "incident", "occurrence", "happening", "activity" (PROV), "episode".
- **Ambigüedades:** granularidad temporal (instante vs intervalo); evento como hecho del mundo vs evento como afirmación sobre el mundo; solapa con "Activity (PROV)".
- **Diferencias entre disciplinas:** CIDOC CRM y la historiografía centran el modelo en eventos; PROV habla de "Activity"; forense de "event timeline"; inteligencia de "incidentes".

#### Relationship
- **Definición:** Vínculo o asociación entre dos o más entidades/conceptos.
- **Contextos de uso:** Modelado E-R; KG (aristas/predicados, tripleta sujeto-predicado-objeto); análisis de redes (link analysis); inteligencia (vínculos entre actores).
- **Variantes:** "link", "association", "edge", "predicate", "tie", "connection".
- **Ambigüedades:** ¿la relación es de primera clase (tiene atributos/identidad) o solo un enlace? Dirección y cardinalidad; relación afirmada vs relación inferida.
- **Diferencias entre disciplinas:** KG/RDF: predicado en una tripleta; análisis de redes: arista (posiblemente ponderada); E-R: relación con cardinalidad; inteligencia: vínculo con fiabilidad.

### D. Contenedores de investigación

#### Case
- **Definición:** Unidad de trabajo que agrupa todo lo relativo a un asunto concreto investigado (materiales, actores, eventos, conclusiones).
- **Contextos de uso:** Derecho/policía (expediente/caso); case management; gestión clínica/social (caso); soporte (ticket/caso).
- **Variantes:** "matter" (legal), "file/expediente", "dossier", "docket", "investigation" (a veces sinónimo).
- **Ambigüedades:** "case" vs "investigation": a veces el caso es el *asunto* y la investigación el *proceso*; a veces son lo mismo.
- **Diferencias entre disciplinas:** Derecho: "matter/case" con número de expediente; policía: caso con estado; soporte/CRM: caso como incidencia.

#### Investigation
- **Definición:** Proceso sistemático de indagación dirigido a esclarecer un asunto mediante recogida y análisis de evidencia.
- **Contextos de uso:** Criminología/policía; periodismo de investigación; auditoría/forense; ciencia (indagación).
- **Variantes:** "inquiry", "probe", "research", "examination", "study".
- **Ambigüedades:** proceso vs contenedor (ver "Case"); una investigación puede abarcar varios casos o un caso varias investigaciones.
- **Diferencias entre disciplinas:** Periodismo: proceso editorial con estándares de verificación; policía: procedimiento reglado; ciencia: "research/inquiry".

### E. Conocimiento

#### Knowledge
- **Definición:** Información estructurada, contextualizada y justificada que permite comprender o actuar; en sentido clásico, "creencia verdadera justificada".
- **Contextos de uso:** Gestión del conocimiento (pirámide DIKW: datos→información→conocimiento→sabiduría); KG (conocimiento como grafo de hechos); epistemología.
- **Variantes:** "understanding", "intelligence" (en sentido de producto), "insight", "know-how".
- **Ambigüedades:** frontera difusa con "información"; conocimiento tácito vs explícito; ¿colección de hechos o capacidad de inferir?
- **Diferencias entre disciplinas:** DIKW lo sitúa por encima de la información; KG lo cosifica como hechos conectados; epistemología lo discute como creencia justificada; inteligencia llama "intelligence" al conocimiento accionable derivado del análisis.

---

## 5. Variantes terminológicas (síntesis)

| Concepto | Sinónimos / variantes frecuentes | Falsos amigos / matices |
|---|---|---|
| Document | record, file, artifact, exhibit, item | "record" puede implicar valor oficial/probatorio |
| Source | origin, informant, primary/secondary source, feed | fuente ≠ documento que aporta |
| Collection | corpus, dataset, fonds, series, batch | "fonds" implica procedencia |
| Metadata | attributes, properties, tags | solapa con provenance |
| Provenance | lineage, chain of custody, pedigree, audit trail | alcance: origen vs historia completa |
| Citation | reference, attribution, footnote | citation vs reference según estilo |
| Reference | link, pointer, bibliographic entry | reference vs relationship |
| Annotation | note, tag, label, markup, commentary | dato vs interpretación |
| Evidence | proof, exhibit, indicator, supporting data | "proof" es más fuerte/conclusivo |
| Evidence Item | exhibit, piece of evidence, artifact | granularidad variable |
| Observation | measurement, datum, sighting | neutralidad discutida |
| Fact | ground truth, verified statement | objeto del mundo vs afirmación verificada |
| Claim | assertion, allegation, statement, proposition | matiz "no probado" |
| Assertion | statement, claim, triple (RDF) | acto vs proposición |
| Finding | result, determination, key finding | intermedio vs conclusivo |
| Hypothesis | conjecture, theory, working hypothesis | hypothesis vs theory |
| Conclusion | verdict, judgment, inference, determination | provisional vs definitiva |
| Entity | object, node, thing, named entity, resource | sentido PROV ≠ sentido E-R |
| Actor | agent, party, person of interest, participant | persona vs agente genérico |
| Event | incident, occurrence, activity, episode | hecho vs afirmación de hecho |
| Relationship | link, edge, predicate, association, tie | enlace vs relación de primera clase |
| Case | matter, file, dossier, docket | case vs investigation |
| Investigation | inquiry, probe, research, examination | proceso vs contenedor |
| Knowledge | understanding, intelligence, insight | conocimiento vs información |

---

## 6. Ambigüedades detectadas (transversales)

1. **Continuo epistémico Observation → Claim → Fact → Finding → Conclusion.** Las fronteras (¿cuándo una observación se vuelve hecho? ¿cuándo un finding es conclusión?) varían por disciplina y por grado de certeza. No hay corte universal.
2. **Evidence: material vs relación.** "Evidencia" designa tanto el material como la *relación de soporte* entre material y afirmación; además "evidence" (incontable) vs "evidence item" (discreto).
3. **Source: origen vs portador.** "Source" puede ser el autor/origen o el documento que transmite la información.
4. **Document vs Evidence Item vs Observation.** El mismo material puede leerse como documento (contenedor), como ítem de evidencia (unidad probatoria) o como observación (constatación), según el rol que se le asigne.
5. **Fact vs Claim corroborado.** El umbral para llamar "hecho" a una afirmación verificada es disciplinar y graduable.
6. **Claim vs Assertion vs Statement.** Casi intercambiables; el matiz distintivo (no-probado / acto de afirmar / atribuible a un emisor) no siempre está presente.
7. **Case vs Investigation.** Asunto (contenedor) vs proceso (indagación); relación de cardinalidad no fija.
8. **Entity vs Actor vs Agent.** "Actor/Agent" como subconjunto de "Entity"; PROV "Agent" y UML "Actor" tienen sentidos técnicos distintos.
9. **Event vs Activity.** "Event" (suceso) vs "Activity" (PROV); granularidad instante/intervalo.
10. **Relationship: enlace vs primera clase.** ¿La relación tiene identidad y atributos, o es un mero vínculo? Afirmada vs inferida.
11. **Metadata vs Provenance vs Annotation.** Las tres describen "algo sobre algo"; sus fronteras se solapan.
12. **Citation vs Reference.** Inversión de significados según la tradición (estilo de cita).
13. **Knowledge vs Information.** Frontera difusa (DIKW) y dependiente de contexto.
14. **Finding vs Conclusion.** Grado de finalidad/confianza no estandarizado.

---

## 7. Comparativa entre disciplinas

Cómo enmarca cada disciplina el eje central del dominio (síntesis, no exhaustiva):

| Disciplina | Concepto eje | Énfasis distintivo | Tratamiento de la certeza |
|---|---|---|---|
| **Digital Forensics** | Evidence Item / Artifact | Integridad y **cadena de custodia**; reproducibilidad técnica | Admisibilidad; integridad (hash) |
| **Intelligence Analysis** | Source + Hypothesis | **Fiabilidad de fuente** vs credibilidad de información; hipótesis competidoras (ACH) | Niveles de confianza explícitos; escalas (Almirantazgo/NATO) |
| **Investigative Journalism** | Source + Fact/Claim | **Atribución** y verificación cruzada; corroboración por múltiples fuentes | Verificación; grados de atribución |
| **Scientific Research** | Hypothesis + Observation | Falsabilidad; reproducibilidad; **peso de la evidencia** | Significación; revisión por pares |
| **Evidence Management** | Evidence Item / Exhibit | Identificación, custodia y trazabilidad de exhibits | Cadena de custodia |
| **Knowledge Graphs** | Entity + Relationship | **Tripletas** (sujeto-predicado-objeto); inferencia; ontologías | Afirmaciones atribuibles; (a veces) confianza por arista |
| **Provenance Models** | Provenance (Entity/Activity/Agent) | **Linaje** y derivación; quién/qué/cuándo | Trazabilidad del origen |
| **Records & Archives** | Document / Record | **Principio de procedencia**, orden original, valor probatorio | Autenticidad e integridad del record |

Observación transversal: ninguna disciplina cubre todo el vocabulario por igual; cada una **profundiza en una parte** y nombra el resto de forma laxa.

---

## 8. Observaciones

- **No existe un vocabulario único** compartido por las ocho disciplinas; hay solapamientos y conflictos de uso reales. Cualquier modelo posterior deberá **elegir y definir** sus términos, consciente de estas variantes.
- **La certeza es graduable y central**: casi todos los conceptos epistémicos (claim/fact/finding/conclusion) se distinguen por *grado de respaldo*, no por categoría tajante.
- **La procedencia es el hilo conductor** entre disciplinas (custodia forense, linaje de datos, principio de procedencia archivística, PROV): es el concepto mejor formalizado y más transversal.
- **La separación hecho/interpretación** (ya señalada en WP-0007) reaparece aquí como tensión entre Observation/Fact (constatación) y Claim/Finding/Conclusion (interpretación).
- **Los contenedores (Case/Investigation/Collection)** se solapan y su relación es disciplinar; convendrá clarificarla.
- Este documento **no resuelve** ninguna de estas tensiones: las expone para el diseño.

---

## 9. Preguntas abiertas para el Principal Architect

1. ¿Qué término adoptará el proyecto para la **unidad mínima de evidencia** y con qué granularidad (frase, afirmación, documento, objeto)?
2. ¿Se distinguirá explícitamente **Observation/Fact (constatación)** de **Claim/Finding/Conclusion (interpretación)**, y dónde se traza la línea?
3. ¿"**Source**" designará el origen (autor/agente), el documento portador, o ambos con términos separados?
4. ¿"**Case**" e "**Investigation**" serán conceptos distintos (asunto vs proceso) o uno solo?
5. ¿Las **Relationships** serán de primera clase (con atributos/identidad y posible fiabilidad) o simples enlaces?
6. ¿Cómo se representará la **certeza/fiabilidad** (de la fuente, de la información, de las conclusiones) y con qué escala?
7. ¿"**Evidence**" se entenderá como material, como relación de soporte, o se separarán ambos sentidos?
8. ¿Qué papel tendrán **Annotation/Metadata/Provenance** y cómo se delimitarán entre sí?
9. ¿Se adoptará algún **vocabulario/estándar externo** (p. ej. PROV, Dublin Core, CIDOC CRM) como referencia terminológica, o un glosario propio?
10. ¿"**Knowledge**" será un artefacto explícito (grafo de hechos) o una propiedad emergente de las conclusiones?

---

## 10. Referencias bibliográficas

> Fuentes canónicas por disciplina, citadas por su nombre reconocido para verificación por el Principal Architect. No se reproduce su contenido ni se infieren citas literales.

- **Provenance:** W3C *PROV Data Model* y *PROV-O* (Entity / Activity / Agent).
- **Metadata / bibliografía:** *Dublin Core Metadata Initiative (DCMI)*; *FRBR* / *IFLA Library Reference Model* (Work / Expression / Manifestation / Item).
- **Archives & Records:** *OAIS Reference Model* (ISO 14721); *ISO 15489 — Records Management*; principio archivístico de *procedencia* y *orden original*.
- **Cultural heritage / eventos:** *CIDOC Conceptual Reference Model (CIDOC CRM)*.
- **Argumentación:** S. Toulmin, *The Uses of Argument* (claim / grounds / warrant / backing / qualifier / rebuttal); J. H. Wigmore, *Wigmore charts* (análisis de evidencia jurídica).
- **Intelligence Analysis:** R. J. Heuer Jr., *Psychology of Intelligence Analysis*; *Analysis of Competing Hypotheses (ACH)*; *Admiralty/NATO System* de fiabilidad de fuente y credibilidad de información.
- **Digital Forensics:** *NIST SP 800-86* (guía de forense digital); principio de intercambio de *Locard*; *cadena de custodia*.
- **Scientific method:** literatura estándar sobre hipótesis, observación, falsabilidad (p. ej. K. Popper) y peso de la evidencia.
- **Knowledge representation:** *RDF* y modelo de *tripleta* (sujeto-predicado-objeto); *schema.org*; teoría de *ontologías* en web semántica.
- **Knowledge management:** jerarquía *DIKW* (Data–Information–Knowledge–Wisdom; R. Ackoff y desarrollos posteriores).
- **Investigative journalism:** manuales de verificación y atribución (p. ej. *The Verification Handbook*) y estándares de *fact-checking*.

---

_Fin de la investigación. No contiene diseño de dominio, modelado DDD, decisiones de arquitectura ni propuestas de implementación. Su único fin es servir de base para ARCH-0002 — Domain Philosophy y RFC-0002 — Domain Model._
