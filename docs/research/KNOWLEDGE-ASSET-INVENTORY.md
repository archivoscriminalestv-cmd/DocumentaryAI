# KNOWLEDGE ASSET INVENTORY — DocumentaryAI (WP-0016)

| Campo | Valor |
|---|---|
| **Document ID** | RES-KNOWLEDGE-ASSET-INVENTORY |
| **Title** | Knowledge Asset Inventory — DocumentaryAI |
| **Status** | Draft (inventory) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | WP-0007 … WP-0015 (ver §5) |

> **Documento inventario.** Lista los **tipos de activos de conocimiento** identificados durante Discovery, derivados **exclusivamente** de WP-0007 a WP-0015.
> **No** introduce conceptos ni categorías nuevos, **no** interpreta el dominio, **no** propone arquitectura/modelos/entidades/DDD, **no** realiza clasificaciones normativas, **no** introduce "Knowledge Capital" ni ningún concepto arquitectónico no aprobado, **no** modifica documentos existentes.
> Solo se inventarían activos que **aparecen** en la documentación; cada uno se cita con su fuente.

---

## 1. Objetivo y alcance

Inventariar, como base documental para la futura arquitectura, los tipos de activos de conocimiento que la fase Discovery identificó. Para cada activo se da: **definición resumida** (derivada de la documentación), **documento(s) fuente** y **papel** dentro del proceso de investigación descrito.

> **Nota sobre la agrupación.** Los activos se ordenan por su **procedencia documental** dentro de Discovery (unidades del dominio · artefactos de investigación · artefactos de producción · criterios y trazabilidad). Esta ordenación es **organizativa y descriptiva**, tomada de cómo los propios documentos agrupan su contenido; **no** constituye una clasificación normativa ni una categoría nueva.

---

## 2. Inventario de tipos de activos

### A. Unidades de conocimiento del dominio
*(aparecen definidas en WP-0009 y usadas en WP-0007/0010/0011/0012/0013)*

- **Evidencia** — Información o material que tiende a apoyar o refutar una afirmación/hipótesis; tratada como **rol relacional**. *Fuente:* WP-0007, WP-0009, WP-0010, WP-0011, WP-0012, WP-0013. *Papel:* sustrato sobre el que se verifica, analiza y concluye.
- **Observación** — Constatación directa de un hecho previa a su interpretación. *Fuente:* WP-0009, WP-0012, WP-0013. *Papel:* dato de partida del bloque de investigación.
- **Afirmación (Claim)** — Enunciado propuesto como verdadero, sujeto a respaldo. *Fuente:* WP-0009, WP-0010, WP-0011, WP-0013. *Papel:* objeto de verificación y de trazabilidad afirmación↔fuente.
- **Hecho (Fact)** — Afirmación tenida por verdadera/verificable; umbral variable por disciplina. *Fuente:* WP-0009, WP-0010, WP-0011. *Papel:* resultado consolidado de la verificación.
- **Hallazgo (Finding)** — Resultado de un análisis. *Fuente:* WP-0009, WP-0010, WP-0011, WP-0012. *Papel:* producto del análisis, alimenta conclusiones.
- **Hipótesis** — Explicación tentativa contrastable. *Fuente:* WP-0007, WP-0009, WP-0010, WP-0012, WP-0013. *Papel:* guía de la investigación; objeto de descarte/confirmación.
- **Conclusión** — Afirmación final derivada del razonamiento. *Fuente:* WP-0009, WP-0010. *Papel:* cierre del razonamiento sobre la evidencia.
- **Conocimiento / base de conocimiento** — Información estructurada, contextualizada y justificada. *Fuente:* WP-0009, WP-0010, WP-0012, WP-0013. *Papel:* consolidación del caso, base de la narrativa.
- **Procedencia (Provenance)** — Registro del origen e historia de un material/afirmación. *Fuente:* WP-0007, WP-0009, WP-0011, WP-0013. *Papel:* trazabilidad y credibilidad (consenso alto en WP-0011).
- **Metadatos** — Datos que describen otros datos/recursos. *Fuente:* WP-0009. *Papel:* descripción y gestión de materiales/fuentes.
- **Relación (corrobora/contradice)** — Vínculo entre piezas de conocimiento. *Fuente:* WP-0007, WP-0009, WP-0011, WP-0013, WP-0014. *Papel:* conecta evidencia, entidades y afirmaciones.
- **Cronología** — Línea temporal de eventos. *Fuente:* WP-0009, WP-0012. *Papel:* producto del análisis del caso.
- **Contradicción** — Conflicto detectado entre piezas de conocimiento. *Fuente:* WP-0009, WP-0012. *Papel:* resultado del análisis; señala incertidumbre.
- **Nivel de confianza / incertidumbre** — Grado de certeza asociado a fuente/afirmación/conclusión. *Fuente:* WP-0010, WP-0011, WP-0013. *Papel:* califica el conocimiento.

### B. Artefactos de investigación / meta-conocimiento
*(producidos por los propios WP de Discovery)*

- **Ontología / definiciones de conceptos** — Recopilación de definiciones, variantes y ambigüedades de conceptos del dominio. *Fuente:* WP-0009. *Papel:* base terminológica de Discovery.
- **Patrones (epistémicos)** — Patrones recurrentes en cómo las disciplinas construyen conocimiento. *Fuente:* WP-0010, WP-0011 (síntesis). *Papel:* repertorio comparado de referencia.
- **Matriz (síntesis / trazabilidad)** — Tabla que cruza temas/activos con sus fuentes y consenso. *Fuente:* WP-0011, WP-0013, WP-0014, WP-0015. *Papel:* consolidar evidencia y trazarla.
- **Capacidad (capability)** — Algo que el proceso/sistema debe poder hacer. *Fuente:* WP-0012, WP-0013, WP-0014. *Papel:* unidad del inventario del MVP.
- **Mapa de dependencias** — Estructura de relaciones funcionales entre capacidades. *Fuente:* WP-0014. *Papel:* visión estructurada previa al diseño.
- **Índice / consolidación** — Documento que organiza y referencia otros. *Fuente:* WP-0015 (y `Architecture-Index.md` como contexto). *Papel:* punto de entrada y navegación.
- **Glosario / variantes terminológicas** — Términos y sus acepciones. *Fuente:* WP-0009, WP-0015. *Papel:* vocabulario común de consulta.
- **Preguntas abiertas** — Cuestiones sin resolver señaladas para el Architect. *Fuente:* WP-0009, WP-0010, WP-0011. *Papel:* agenda de decisiones pendientes.
- **Referencias bibliográficas** — Fuentes canónicas citadas por disciplina. *Fuente:* WP-0009, WP-0010. *Papel:* respaldo verificable de la investigación.

### C. Artefactos del proceso de producción documental
*(identificados en WP-0012 y reutilizados en WP-0013)*

- **Lista de fuentes** — Inventario de fuentes candidatas con metadatos. *Fuente:* WP-0012, WP-0013. *Papel:* materia prima del documental.
- **Notas / material recopilado** — Documentos, transcripciones, capturas. *Fuente:* WP-0012, WP-0013. *Papel:* base documental recogida.
- **Guion** — Texto narrado del documental, con referencias afirmación↔fuente. *Fuente:* WP-0012, WP-0013. *Papel:* contenido del vídeo.
- **Storyboard** — Plan visual del guion. *Fuente:* WP-0012, WP-0013. *Papel:* puente guion↔producción.
- **Recursos (assets) visuales/sonoros** — Imágenes, clips, gráficos, música, SFX. *Fuente:* WP-0012, WP-0013. *Papel:* material audiovisual del montaje.
- **Vídeo final** — Pieza exportada para publicación. *Fuente:* WP-0012, WP-0013. *Papel:* salida principal del proceso.
- **Métricas** — Datos de desempeño de la plataforma/audiencia. *Fuente:* WP-0012, WP-0013. *Papel:* base del aprendizaje.
- **Lecciones aprendidas** — Conclusiones del ciclo para mejorar los siguientes. *Fuente:* WP-0012, WP-0013. *Papel:* cierre del bucle de aprendizaje.

### D. Activos de criterio y trazabilidad

- **Criterios (selección / aceptación / clasificación)** — Reglas para seleccionar tema, aceptar entregables o clasificar capacidades. *Fuente:* WP-0012 (selección), WP-0013 (clasificación funcional), criterios de aceptación en varios WP. *Papel:* guían decisiones documentadas (sin ser, aquí, decisiones de arquitectura).
- **Dependencias (registro de)** — Prerrequisitos funcionales entre activos/capacidades. *Fuente:* WP-0013, WP-0014. *Papel:* trazar qué habilita a qué.

> **Sobre "taxonomías":** el ejemplo del WP menciona "taxonomías". En Discovery aparecen **agrupaciones descriptivas** (p. ej. los enfoques "centric" en WP-0007; las agrupaciones de conceptos/capacidades en WP-0009/0012/0013), pero **no** una taxonomía normativa establecida. Se registran como agrupaciones descriptivas, no como un activo "taxonomía" formal, para no crear una categoría nueva.

---

## 3. Tabla de trazabilidad (activo → documentos donde aparece)

| Activo | WP-0007 | WP-0009 | WP-0010 | WP-0011 | WP-0012 | WP-0013 | WP-0014 | WP-0015 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Evidencia | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ |
| Observación | | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ |
| Afirmación (Claim) | | ✓ | ✓ | ✓ | | ✓ | | ✓ |
| Hecho (Fact) | ✓ | ✓ | ✓ | ✓ | | | | ✓ |
| Hallazgo (Finding) | | ✓ | ✓ | ✓ | ✓ | | | ✓ |
| Hipótesis | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ |
| Conclusión | | ✓ | ✓ | ✓ | | | | ✓ |
| Conocimiento | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ |
| Procedencia | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Metadatos | | ✓ | | ✓ | ✓ | | | ✓ |
| Relación | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | |
| Cronología | | ✓ | | | ✓ | ✓ | | |
| Contradicción | | ✓ | ✓ | ✓ | ✓ | ✓ | | |
| Confianza/incertidumbre | | | ✓ | ✓ | ✓ | ✓ | | |
| Ontología/definiciones | | ✓ | | ✓ | | | | ✓ |
| Patrones | | | ✓ | ✓ | | | | ✓ |
| Matriz (síntesis/trazab.) | | | | ✓ | | ✓ | ✓ | ✓ |
| Capacidad | | | | | ✓ | ✓ | ✓ | ✓ |
| Mapa de dependencias | | | | | | ✓ | ✓ | ✓ |
| Índice/consolidación | | | | | | | | ✓ |
| Glosario | | ✓ | | | | | | ✓ |
| Preguntas abiertas | ✓ | ✓ | ✓ | ✓ | | ✓ | | |
| Referencias bibliográficas | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lista de fuentes | | ✓ | | | ✓ | ✓ | | |
| Notas/material | | ✓ | | | ✓ | ✓ | | |
| Guion | | | | | ✓ | ✓ | | |
| Storyboard | | | | | ✓ | ✓ | | |
| Recursos (assets) | | | | | ✓ | ✓ | | |
| Vídeo final | | | | | ✓ | ✓ | | |
| Métricas | | | | | ✓ | ✓ | | |
| Lecciones aprendidas | | | | | ✓ | ✓ | | |
| Criterios | | | | | ✓ | ✓ | | ✓ |
| Dependencias (registro) | | | | | | ✓ | ✓ | ✓ |

> La marca ✓ indica aparición del activo en ese WP (uso o definición). Derivado del contenido de cada documento; sin inferencias añadidas.

---

## 4. Observaciones descriptivas sobre reutilización

> Únicamente cuando la reutilización **se infiere directamente** de la documentación citada. No son propuestas.

- **Procedencia:** WP-0012 (C-30 implícito en artefactos) y WP-0013 (CAP-30: "trazabilidad reutilizable") la describen como **reutilizable** dentro y entre proyectos.
- **Conocimiento / base de conocimiento:** WP-0009 (DIKW) y WP-0012/WP-0013 (C-10/CAP-10: "conocimiento reutilizable entre proyectos") lo describen como **reutilizable** más allá de un único documental.
- **Recursos (assets):** WP-0012 (C-16: "reutilización de assets") los describe como **reutilizables**.
- **Lecciones aprendidas:** WP-0012/WP-0013 las describen alimentando la Ideación (C-29→C-01 / CAP-29→CAP-01), es decir, **reutilizadas** en ciclos posteriores.
- **Capacidades y mapa de dependencias:** WP-0013/WP-0014 son **reutilizados** explícitamente como base de ARCH-0003 (según sus propios objetivos).
- **Matrices e índices:** WP-0011/WP-0015 declaran su finalidad de **reducir la carga de consulta**, es decir, reutilización como apoyo de diseño.
- **Esquemas de organización / criterios:** WP-0012 (C-07: organización reutilizable; criterios de selección) describen reutilización de criterios y taxonomías de organización entre proyectos.

No se registran observaciones de reutilización para activos donde la documentación no la afirma directamente.

---

## 5. Referencias cruzadas

- WP-0007 · `docs/architecture/Evidence-Centric-Domain-Research.md`
- WP-0009 · `docs/research/DOMAIN-ONTOLOGY-RESEARCH.md`
- WP-0010 · `docs/research/EPISTEMIC-DOMAIN-PATTERN-RESEARCH.md`
- WP-0011 · `docs/research/DOMAIN-EVIDENCE-SYNTHESIS-MATRIX.md`
- WP-0012 · `docs/research/YOUTUBE-DOCUMENTARY-PRODUCTION-CAPABILITY-MAP.md`
- WP-0013 · `docs/research/MVP-CAPABILITY-INVENTORY.md`
- WP-0014 · `docs/research/CAPABILITY-DEPENDENCY-MAP.md`
- WP-0015 · `docs/research/DISCOVERY-INDEX.md`

---

_Fin del inventario. Documento exclusivamente derivado de WP-0007…WP-0015: no introduce conceptos ni categorías nuevos, no interpreta el dominio, no realiza clasificaciones normativas, no introduce "Knowledge Capital" ni otros conceptos arquitectónicos, no propone modelos/componentes/entidades/DDD/arquitectura ni decisiones de diseño, y no modifica documentos existentes._
