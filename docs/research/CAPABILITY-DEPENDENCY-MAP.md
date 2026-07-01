# CAPABILITY DEPENDENCY MAP — DocumentaryAI (WP-0014)

| Campo | Valor |
|---|---|
| **Document ID** | RES-CAPABILITY-DEPENDENCY-MAP |
| **Title** | Capability Dependency Map — DocumentaryAI |
| **Status** | Draft (synthesis) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | `docs/research/MVP-CAPABILITY-INVENTORY.md` (WP-0013) |

> **Documento de síntesis (Sprint A-02 — MVP Definition).** Mapa de **dependencias funcionales** entre las capacidades de WP-0013.
> **No** diseña arquitectura, componentes, servicios, módulos, agentes, capas, APIs, Bounded Contexts, Aggregate Roots ni entidades; **no** propone implementación; **no** modifica la clasificación de WP-0013 ni redefine capacidades; **no** decide.
> Reorganiza y analiza, en términos puramente funcionales, la información de dependencias ya contenida en WP-0013.

---

## 1. Objetivo

Ofrecer al Principal Architect una **visión estructurada** de cómo se relacionan funcionalmente las capacidades del MVP (qué habilita a qué, qué es transversal, qué forma ciclos), como apoyo previo a ARCH-0003 — MVP Capability Architecture.

El documento **no** diseña el sistema: hace explícita la **estructura de dependencias** ya descrita en WP-0013.

---

## 2. Alcance

- Fuente **única**: `MVP-CAPABILITY-INVENTORY.md` (WP-0013). Sin investigación nueva.
- Se reutilizan, sin alterarlos, los **identificadores, nombres, clasificación y dependencias** de WP-0013.
- Se elaboran: agrupaciones funcionales, dependencias directas en ambos sentidos, capacidades transversales, habilitadoras, consumidoras, ciclos funcionales y capacidades independientes.
- Fuera de alcance: cualquier diseño, capa, servicio, API, tecnología o decisión.

> Nota de consistencia: las dependencias aquí mostradas son las **declaradas en WP-0013** (cadena principal + transversales). No se añaden ni se eliminan relaciones.

---

## 3. Agrupaciones funcionales

> Las mismas agrupaciones de WP-0013 (no se redefine nada).

| Grupo | Capacidades |
|---|---|
| **G1 · Investigación** | CAP-01…CAP-10 |
| **G2 · Narrativa** | CAP-11…CAP-15 |
| **G3 · Producción / Post** | CAP-16…CAP-20 |
| **G4 · Publicación** | CAP-21…CAP-25 |
| **G5 · Post-publicación / Aprendizaje** | CAP-26…CAP-29 |
| **G6 · Transversales (dominio + contenedor)** | CAP-30, CAP-31, CAP-32, CAP-33 |

Lectura de alto nivel: G1→G2→G3→G4→G5 forman la **cadena de producción**, mientras G6 **atraviesa** varios grupos (procedencia, evidencia, incertidumbre, contenedor de proyecto).

---

## 4. Dependencias entre capacidades

> "Depende de" = prerrequisitos funcionales (de WP-0013). "Habilita a" = capacidades que la tienen como prerrequisito (relación inversa derivada).

| Capacidad | Depende de | Habilita a |
|---|---|---|
| CAP-01 Ideación | — (realimentada por CAP-29) | CAP-02 |
| CAP-02 Selección de tema | CAP-01 | CAP-03, CAP-33 (contiene) |
| CAP-03 Objetivos | CAP-02 | CAP-04, CAP-11 |
| CAP-04 Plan de investigación | CAP-03 | CAP-05 |
| CAP-05 Descubrimiento de fuentes | CAP-04 | CAP-06, CAP-23 |
| CAP-06 Recolección | CAP-05, CAP-30 | CAP-07, CAP-30, CAP-31 |
| CAP-07 Organización | CAP-06 | CAP-08 |
| CAP-08 Verificación | CAP-07, CAP-31, CAP-32 | CAP-09, CAP-19 |
| CAP-09 Análisis | CAP-08, CAP-30, CAP-31 | CAP-10 |
| CAP-10 Construcción de conocimiento | CAP-09, CAP-30, CAP-31, CAP-32 | CAP-11 |
| CAP-11 Diseño narrativo | CAP-10, CAP-03 | CAP-12, CAP-21 |
| CAP-12 Estructura | CAP-11 | CAP-13 |
| CAP-13 Guion | CAP-12, CAP-30, CAP-31 | CAP-14, CAP-17, CAP-22 |
| CAP-14 Storyboard | CAP-13 | CAP-15, CAP-18 |
| CAP-15 Planificación visual | CAP-14 | CAP-16 |
| CAP-16 Producción de recursos | CAP-15, CAP-23 | CAP-18, CAP-23 |
| CAP-17 Locución | CAP-13 | CAP-18 |
| CAP-18 Edición | CAP-16, CAP-17, CAP-14 | CAP-19 |
| CAP-19 Control de calidad | CAP-18, CAP-08 | CAP-20 (correcciones → CAP-18) |
| CAP-20 Exportación | CAP-19 | CAP-21, CAP-22, CAP-24 |
| CAP-21 Empaquetado | CAP-11, CAP-20 | CAP-24 |
| CAP-22 Metadatos / SEO | CAP-13, CAP-20 | CAP-24 |
| CAP-23 Derechos | CAP-05, CAP-16 | CAP-16, CAP-24 |
| CAP-24 Publicación | CAP-20, CAP-21, CAP-22, CAP-23 | CAP-25, CAP-26, CAP-28 |
| CAP-25 Distribución | CAP-24 | — (terminal) |
| CAP-26 Métricas | CAP-24 | CAP-27 |
| CAP-27 Retroalimentación | CAP-26, CAP-28 | CAP-29 |
| CAP-28 Comunidad | CAP-24 | CAP-27, CAP-29 |
| CAP-29 Aprendizaje | CAP-27, CAP-28 | CAP-01 (realimenta) |
| CAP-30 Procedencia | CAP-06 (origen) | CAP-08, CAP-09, CAP-10, CAP-13 |
| CAP-31 Afirmaciones/evidencia | CAP-06 (origen) | CAP-08, CAP-09, CAP-10, CAP-13 |
| CAP-32 Incertidumbre/confianza | CAP-31 | CAP-08, CAP-10 |
| CAP-33 Proyecto/caso | CAP-02 | contiene CAP-04…CAP-29 (foundational) |

---

## 5. Capacidades transversales

> Capacidades que atraviesan varios grupos en lugar de ocupar un único punto de la cadena (declaradas transversales en WP-0013).

| Capacidad | Atraviesa | Naturaleza transversal |
|---|---|---|
| **CAP-30 Procedencia** | G1 y G2 (CAP-06→CAP-08/09/10/13) | Acompaña a materiales y afirmaciones a lo largo de investigación y guion |
| **CAP-31 Afirmaciones/evidencia** | G1 y G2 (CAP-06→CAP-08/09/10/13) | Sustrato de evidencia compartido por verificación, análisis, conocimiento y guion |
| **CAP-32 Incertidumbre/confianza** | G1 (CAP-08, CAP-10) | Califica afirmaciones/conclusiones en distintos puntos |
| **CAP-23 Derechos** | G1, G3, G4 (CAP-05, CAP-16, y puerta a CAP-24) | Comprobación de cumplimiento en fuentes, recursos y publicación |
| **CAP-33 Proyecto/caso** | Todos los grupos | Contenedor que sostiene CAP-04…CAP-29 |

---

## 6. Capacidades habilitadoras

> Capacidades de las que **dependen muchas otras** (mayor número de capacidades habilitadas / mayor alcance aguas abajo). Derivado de la columna "Habilita a".

| Capacidad | Habilita (directas) | Por qué es habilitadora |
|---|---|---|
| **CAP-33 Proyecto/caso** | Contiene CAP-04…CAP-29 | Sin contenedor no se sostiene ninguna otra del ciclo |
| **CAP-06 Recolección** | CAP-07, CAP-30, CAP-31 | Origen de materiales y del sustrato de evidencia/procedencia |
| **CAP-30 Procedencia** | CAP-08, CAP-09, CAP-10, CAP-13 | Habilita verificación, análisis, conocimiento y guion |
| **CAP-31 Afirmaciones/evidencia** | CAP-08, CAP-09, CAP-10, CAP-13 | Sustrato del que parten verificación, análisis, conocimiento y guion |
| **CAP-13 Guion** | CAP-14, CAP-17, CAP-22 | Punto del que derivan producción visual, locución y metadatos |
| **CAP-20 Exportación** | CAP-21, CAP-22, CAP-24 | Habilita empaquetado, metadatos y publicación |
| **CAP-24 Publicación** | CAP-25, CAP-26, CAP-28 | Habilita todo el bloque de aprendizaje (métricas, distribución, comunidad) |

Observación (descriptiva): las habilitadoras se concentran en **el contenedor (CAP-33)**, **el sustrato de evidencia (CAP-06/30/31)** y los **puntos de bifurcación** de la cadena (CAP-13, CAP-20, CAP-24).

---

## 7. Capacidades consumidoras

> Capacidades que **dependen de varias** (mayor número de prerrequisitos) y/o producen valor terminal. Derivado de la columna "Depende de".

| Capacidad | Depende de (nº) | Carácter consumidor |
|---|---|---|
| **CAP-24 Publicación** | CAP-20, CAP-21, CAP-22, CAP-23 (4) | Converge toda la cadena de publicación |
| **CAP-10 Construcción de conocimiento** | CAP-09, CAP-30, CAP-31, CAP-32 (4) | Consume todo el sustrato de evidencia del bloque G1 |
| **CAP-18 Edición** | CAP-16, CAP-17, CAP-14 (3) | Converge producción de recursos, locución y storyboard |
| **CAP-08 Verificación** | CAP-07, CAP-31, CAP-32 (3) | Consume material y sustrato de evidencia/confianza |
| **CAP-29 Aprendizaje** | CAP-27, CAP-28 (2) | Consumidor **terminal**: cierra el ciclo |
| **CAP-25 Distribución** | CAP-24 (1) | Consumidor terminal (sin salidas hacia otras) |

Observación: los grandes **puntos de convergencia** son CAP-10 (cierre del conocimiento), CAP-18 (ensamblaje), CAP-24 (publicación) y CAP-29 (aprendizaje terminal).

---

## 8. Ciclos funcionales

> Identificación de posibles ciclos a partir de las relaciones de WP-0013. No se diseñan; se constatan.

1. **Bucle de aprendizaje (macro)** — el único ciclo de alcance global:
   `CAP-24 → CAP-26 → CAP-27 → CAP-29 → CAP-01 → CAP-02 → … → CAP-24` (con CAP-28 alimentando CAP-27 y CAP-29).
   Es el ciclo que materializa el propósito del MVP ("aprender e iterar").

2. **Bucle de revisión (local)** — posible, derivado de que CAP-19 produce "correcciones":
   `CAP-18 → CAP-19 → (correcciones) → CAP-18`.
   Iteración de calidad antes de exportar.

Fuera de estos dos, el resto del grafo es **acíclico** (cadena dirigida G1→…→G5). Las capacidades transversales (G6) no introducen ciclos: aportan sustrato en una sola dirección.

---

## 9. Capacidades independientes

> Capacidades sin prerrequisitos funcionales y/o sin conexión fuerte con el resto.

- **Sin prerrequisitos aguas arriba:** únicamente **CAP-01 Ideación** (no depende de ninguna; solo es *realimentada* por CAP-29 a través del bucle de aprendizaje). Funciona como **punto de entrada** del ciclo.
- **Capacidad foundational:** **CAP-33 Proyecto/caso** actúa como contenedor raíz; aunque WP-0013 la vincula a CAP-02, su papel es **sostener** al resto más que depender de ellas.
- **Plenamente aisladas (sin dependencias ni dependientes):** **ninguna**. El conjunto está **altamente interconectado**; no hay capacidades sueltas.

---

## 10. Observaciones

- El grafo de capacidades es **mayoritariamente una cadena dirigida** con dos ciclos: uno **global** (aprendizaje) y uno **local** (revisión de calidad).
- Los **cuellos de habilitación** se concentran en CAP-33 (contenedor), el **sustrato de evidencia** (CAP-06/30/31) y los **bifurcadores** CAP-13, CAP-20 y CAP-24: muchas capacidades dependen de ellos.
- Las **transversales** (procedencia, evidencia, incertidumbre, derechos, contenedor) cruzan grupos sin generar ciclos, lo que las hace candidatas naturales a recibir atención temprana (observación funcional, **no** decisión arquitectónica).
- La estructura es **coherente con la clasificación de WP-0013**: casi todas las habilitadoras y consumidoras críticas están entre las capacidades marcadas **Esenciales**; las dos **Fuera del MVP** (CAP-25, CAP-28) son terminales o secundarias en el grafo.
- Todo deriva de WP-0013; **no** se ha añadido ni modificado información.

---

## 11. Referencias

> Fuente única, conforme al WP.

- **WP-0013** — MVP Capability Inventory · `docs/research/MVP-CAPABILITY-INVENTORY.md`
  - (que a su vez referencia WP-0007, WP-0009, WP-0010, WP-0011 y WP-0012).

---

_Fin del mapa de dependencias. Documento de síntesis: basado exclusivamente en WP-0013, sin conocimiento nuevo, sin decisiones, sin diseño de componentes/servicios/módulos/agentes/capas/APIs/Bounded Contexts/Aggregate Roots/entidades, sin modificar la clasificación ni redefinir capacidades. Apoyo directo para ARCH-0003 — MVP Capability Architecture._
