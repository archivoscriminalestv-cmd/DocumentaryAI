# Evidence-Centric Domain — Technical Research (WP-0007)

> **Documento de investigación técnica.** Material de apoyo para la redacción de **RFC-0002 — Domain Model** por parte del Principal Architect.
> **No** diseña DocumentaryAI, **no** define entidades ni Aggregate Roots, **no** propone arquitectura definitiva y **no** es un RFC.
> Rol del autor: *Architecture Research Engineer*. Analiza enfoques y compromisos; las decisiones corresponden al Principal Architect.

---

## Resumen ejecutivo

Existen cuatro grandes "centros de gravedad" para modelar plataformas de investigación: **document-centric**, **case-centric**, **evidence-centric** y **knowledge-centric**. No son mutuamente excluyentes; describen *qué concepto domina el modelo* y, por tanto, alrededor de qué se organizan identidad, ciclo de vida, invariantes y relaciones.

Un dominio **evidence-centric** pone la **unidad de evidencia** (un hecho atestiguado, con procedencia y fiabilidad) en el centro. Aporta gran rigor (trazabilidad, contradicciones, cadena de custodia conceptual) pero introduce complejidad y riesgos notables —especialmente si la evidencia se modela como *Aggregate Root* sin matices—. Esta investigación enumera esos compromisos y alternativas para informar la decisión, sin tomarla.

---

## 1. Qué caracteriza a un dominio *evidence-centric*

Un dominio centrado en evidencia se reconoce por estos rasgos conceptuales:

- **La evidencia es la unidad atómica de verdad.** El modelo gira en torno a afirmaciones/hechos con respaldo, no en torno al contenedor (documento) ni al expediente (caso).
- **Procedencia (provenance) de primera clase.** De cada pieza de evidencia importa *de dónde viene*: fuente, documento origen, ubicación dentro de la fuente, quién/qué la extrajo y cuándo.
- **Fiabilidad y grados de certeza.** La evidencia no es binaria; suele llevar asociada credibilidad, corroboración y posibles conflictos con otra evidencia.
- **Inmutabilidad histórica + interpretación mutable.** El hecho observado tiende a ser inmutable (lo que dijo una fuente), mientras que su interpretación, clasificación o peso evolucionan.
- **Relaciones densas.** La evidencia se conecta con entidades del mundo (personas, lugares, tiempos, eventos), con otras evidencias (corrobora/contradice) y con conclusiones derivadas (hipótesis).
- **Trazabilidad bidireccional.** Desde una conclusión se debe poder volver a la evidencia que la sustenta, y desde una evidencia ver qué conclusiones afecta.
- **Cadena de custodia conceptual.** Aunque no sea forense en sentido legal, interesa registrar cómo una afirmación llegó a estar en el sistema y cómo ha cambiado su estado.

En síntesis: lo evidence-centric prioriza **rigor epistémico y trazabilidad** por encima de la comodidad de gestionar documentos o expedientes.

---

## 2. Diferencias entre enfoques

Comparativa conceptual de los cuatro "centros de gravedad". Se describe *qué es la entidad central* y *cómo se organiza el modelo*, sin definir entidades concretas para DocumentaryAI.

| Enfoque | Entidad central (conceptual) | Pregunta que responde mejor | Unidad de identidad/ciclo de vida |
|---|---|---|---|
| **Document-centric** | El documento/archivo importado | "¿Qué documentos tenemos y qué contienen?" | El documento (versión, almacenamiento, metadatos) |
| **Case-centric** | El caso/expediente de investigación | "¿En qué estado está esta investigación?" | El caso (apertura, progreso, cierre) |
| **Evidence-centric** | La pieza de evidencia/afirmación con procedencia | "¿Qué sabemos, con qué respaldo y qué lo contradice?" | La evidencia (origen, fiabilidad, corroboración) |
| **Knowledge-centric** | El conocimiento conectado (entidades y relaciones, grafo) | "¿Cómo se relaciona todo lo que sabemos?" | El nodo/relación del grafo de conocimiento |

Relación entre ellos (no jerarquía rígida):

- **Document → Evidence:** los documentos son *portadores* de evidencia; lo document-centric trata el contenedor, lo evidence-centric trata el contenido atestiguado.
- **Case → Evidence:** el caso es el *contexto/ámbito*; la evidencia es lo que se acumula dentro.
- **Evidence → Knowledge:** la evidencia individual es el *sustrato*; el conocimiento es la *red emergente* de entidades y relaciones derivadas y corroboradas.

Es habitual que una plataforma madura sea **híbrida**: case-centric en la superficie (cómo trabaja el usuario), evidence-centric en el corazón (cómo se garantiza el rigor) y knowledge-centric en las capacidades analíticas.

---

## 3. Ventajas e inconvenientes de cada enfoque

### Document-centric
- **Ventajas:** simple de implementar; mapea directamente a importación/almacenamiento; intuitivo; buen punto de partida.
- **Inconvenientes:** la "verdad" queda atrapada en los documentos; difícil razonar sobre hechos que aparecen en varias fuentes; contradicciones y cronologías son costosas; escala mal hacia el análisis.

### Case-centric
- **Ventajas:** encaja con el flujo de trabajo real (se investiga "un caso"); ciclo de vida y permisos naturales; buena unidad de organización y acceso.
- **Inconvenientes:** el caso tiende a convertirse en un *aggregate gigante*; el conocimiento queda aislado por caso (silos), dificultando reutilizar evidencia entre investigaciones; el rigor sobre hechos individuales no es el foco.

### Evidence-centric
- **Ventajas:** máximo rigor y trazabilidad; soporta de forma natural contradicciones, corroboración, cronologías y derivación de hipótesis; la procedencia es de primera clase; facilita auditoría.
- **Inconvenientes:** mayor complejidad de modelado; riesgo de granularidad excesiva (todo se vuelve "evidencia"); coste de definir identidad, deduplicación y fiabilidad; curva de adopción más alta.

### Knowledge-centric
- **Ventajas:** potencia analítica (relaciones, inferencia, descubrimiento de vínculos); visión integrada del dominio; muy adecuado para preguntas exploratorias.
- **Inconvenientes:** complejidad alta; riesgo de perder la procedencia si el grafo se desliga de su evidencia de origen; difícil de gobernar y validar; puede mezclar "hecho" con "interpretación" si no se separan capas.

---

## 4. Riesgos de modelar *Evidence* como Aggregate Root

> Análisis de riesgos genérico de DDD. **No** se afirma que DocumentaryAI deba o no hacerlo; es material para que el Principal Architect lo pondere.

1. **Fronteras de consistencia mal dimensionadas.** Un Aggregate Root define un límite transaccional/de invariantes. Si "Evidence" lo es, hay que decidir qué queda dentro (¿procedencia? ¿anotaciones? ¿enlaces a entidades?). Demasiado dentro → agregado pesado y contención; demasiado poco → invariantes que no se pueden garantizar.

2. **Relaciones muchos-a-muchos densas.** La evidencia se corrobora/contradice con otra evidencia y se vincula a múltiples entidades. Los Aggregate Roots no deben referenciarse entre sí por contenido sino por identidad; una red densa de evidencia tensiona esa regla y puede empujar hacia agregados que "se llaman" unos a otros.

3. **Granularidad e identidad.** ¿Qué *es* una unidad de evidencia? ¿Una frase, un párrafo, una afirmación normalizada? Si la identidad es ambigua, surgen duplicados, fusiones y *splits* difíciles de gestionar como raíz de agregado.

4. **Invariantes poco claras.** Un Aggregate Root existe para proteger invariantes. Si las reglas que "siempre deben cumplirse" sobre una evidencia aislada son pocas (y muchas reglas son en realidad *del conjunto*: corroboración, contradicción, cronología), puede que el verdadero límite de consistencia esté en otro concepto, no en la evidencia individual.

5. **Contención y rendimiento.** Si muchas operaciones tocan "la evidencia", convertirla en raíz única puede crear cuellos de botella de concurrencia y bloqueos.

6. **Acoplamiento del análisis al núcleo.** Si la evidencia-raíz arrastra interpretación (fiabilidad calculada, clasificación por IA), se mezcla *hecho inmutable* con *interpretación mutable*, dificultando evolucionar el análisis sin tocar el corazón del dominio.

7. **Trazabilidad vs. inmutabilidad.** Como raíz, hay que decidir cómo se versiona/inmuta; un diseño ingenuo puede perder la historia (qué cambió y por qué) o, al revés, volverlo inmanejable.

---

## 5. Alternativas posibles (genéricas)

Opciones de modelado que el Principal Architect podría considerar (descripción conceptual, no prescripción):

- **Contexto como raíz, evidencia dentro.** Usar un concepto de mayor nivel (p. ej. el ámbito de investigación) como límite de consistencia, con la evidencia como entidad gestionada dentro de ese límite. Mitiga el problema de raíces que se referencian entre sí.
- **Evidencia inmutable + capa de interpretación separada.** Separar el *hecho atestiguado* (inmutable, con procedencia) de su *valoración/clasificación* (mutable, derivada). Permite evolucionar el análisis sin tocar el registro original.
- **Relaciones como ciudadanos de primera clase.** Modelar "corrobora/contradice/relaciona" como conceptos explícitos (no como referencias incrustadas), de modo que la red de evidencia viva fuera de cada agregado.
- **Enfoque por capas/centros combinados.** Case-centric en la organización y permisos; evidence-centric en el rigor; knowledge-centric como proyección analítica derivada (vistas/modelos de lectura), sin que el grafo sea la fuente de verdad.
- **Separación lectura/escritura (estilo CQRS conceptual).** Un modelo de escritura conservador (evidencia + procedencia) y modelos de lectura especializados (cronologías, grafos, contradicciones) construidos a partir de él.
- **Event-sourcing / registro append-only (conceptual).** Tratar la incorporación y cambios de estado de la evidencia como hechos registrados, favoreciendo trazabilidad y cadena de custodia (con su coste de complejidad).

Cada alternativa intercambia **rigor/flexibilidad** por **complejidad**; ninguna es universalmente superior.

---

## 6. Casos conocidos similares (sin copiar arquitectura)

Dominios del mundo real que afrontan retos análogos. Se citan como *referencia de problemas y patrones*, **sin reproducir su arquitectura interna**:

- **e-Discovery / litigation support (legal):** ingestión masiva de documentos, extracción de hechos relevantes, procedencia y privilegios. Tensión clásica document-centric ↔ evidence-centric.
- **Gestión de casos / case management:** expedientes con ciclo de vida, estados y acceso por caso. Ejemplo de superficie case-centric; conocido por el riesgo de silos.
- **Forense digital y cadena de custodia:** inmutabilidad del artefacto original, registro de quién/cuándo/cómo se manipuló; énfasis en procedencia y auditoría.
- **Inteligencia / OSINT y *intelligence analysis*:** afirmaciones con grados de fiabilidad, corroboración entre fuentes, vínculos entre entidades; muy cercano a evidence- y knowledge-centric.
- **Periodismo de investigación y *fact-checking*:** afirmaciones atribuidas a fuentes, verificación, contradicciones y cronologías; rigor de procedencia.
- **Grafos de conocimiento / *knowledge graphs*:** entidades y relaciones como núcleo; potentes para análisis, con el riesgo conocido de desligar el conocimiento de su evidencia de origen.
- **Sistemas de anotación académica y de archivística:** vínculo entre afirmación, cita y ubicación exacta en la fuente (procedencia fina).

Lección transversal: las plataformas maduras casi nunca son "puras"; **combinan centros** y, sobre todo, **protegen la procedencia** como activo crítico.

---

## 7. Recomendaciones para el Principal Architect

> Recomendaciones **de investigación** (qué considerar y qué decidir), no decisiones de diseño.

1. **Definir explícitamente el "centro de gravedad" antes que las entidades.** Decidir si el corazón es evidence-centric (y con qué superficie case-centric) condicionará todo lo demás.
2. **Tratar la procedencia como requisito de primer orden** desde el inicio; es el activo que más cuesta retrofitar y el que diferencia a estas plataformas.
3. **Separar hecho inmutable de interpretación mutable.** Aislar lo atestiguado de su valoración facilita incorporar análisis (incluida IA en fases posteriores) sin contaminar el núcleo.
4. **Cuestionar la identidad y granularidad de la evidencia** antes de elevarla a raíz: ¿qué es una unidad?, ¿cómo se deduplica/fusiona?, ¿qué invariantes propias tiene?
5. **Evaluar el contexto de investigación como posible límite de consistencia**, dejando la evidencia como entidad dentro, frente a hacerla raíz aislada.
6. **Modelar las relaciones (corrobora/contradice) como conceptos explícitos**, no como referencias incrustadas, para soportar la red densa sin romper fronteras de agregado.
7. **Prever proyecciones de lectura** (cronologías, grafos, contradicciones) derivadas del modelo de escritura, en lugar de forzar un único modelo que sirva para todo.
8. **Aplicar evolución progresiva** (principio ya vigente del proyecto): empezar por el centro mínimo viable y dejar que knowledge-centric/análisis emerjan cuando exista necesidad real.
9. **Registrar las decisiones como ADR** y, si procede, validar el modelo con escenarios concretos (cronología, contradicción, hipótesis) antes de fijarlo en RFC-0002.

---

_Fin de la investigación. No define la arquitectura de DocumentaryAI, no establece entidades ni Aggregate Roots, no asume tecnologías y no contiene código._
