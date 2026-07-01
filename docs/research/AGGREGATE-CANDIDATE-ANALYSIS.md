# AGGREGATE CANDIDATE ANALYSIS — Research vs Knowledge Base (WP-0020)

| Campo | Valor |
|---|---|
| **Document ID** | RES-AGGREGATE-CANDIDATE-ANALYSIS |
| **Title** | Aggregate Candidate Analysis — Research vs Knowledge Base |
| **Status** | Draft (analysis) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | ARCH-0002; WP-0007…WP-0019 (ver §8) |

> **Documento de análisis comparativo, exclusivamente recopilatorio.** Compara los dos candidatos a **núcleo del dominio** —**Research** y **Knowledge Base**— a partir **solo** de ARCH-0002 y WP-0007…WP-0019.
> **No** elige ganador, **no** propone arquitectura, **no** define agregados (DDD) y **no** modifica documentos. Toda afirmación se cita a su fuente.

---

## 1. Encuadre

ARCH-0002 sostiene simultáneamente dos principios que dan origen a los dos candidatos:

- **AP-002 — Research Centric:** "All meaningful work belongs to a research process. Research is the fundamental business activity of the platform."
- **AP-001 — Knowledge First:** "Knowledge is the primary product. Content is a derived artifact."

Por eso existen dos candidatos a núcleo: **Research** (la actividad/proceso central) y **Knowledge Base** (el producto acumulado y reutilizable). Este documento recopila la evidencia de cada uno **sin** decidir.

> Distinción operativa observada en la documentación: **Research** tiende a ser **por-proyecto** (unidad de trabajo de una investigación); **Knowledge Base** tiende a ser **transversal/persistente** (acumulación reutilizable entre proyectos).

---

## 2. Evidencias a favor de **Research** como núcleo

- **ARCH-0002 AP-002 (Research Centric):** la investigación es "the fundamental business activity"; "all meaningful work belongs to a research process".
- **ARCH-0002 §3 (Domain Definition):** la plataforma "support[s] the complete lifecycle of documentary research".
- **ARCH-0002 §9 (Success Criteria):** el primer criterio es "a complete research process can be executed".
- **WP-0018 (Research Lifecycle):** todo el flujo se describe como un **ciclo de vida de investigación** (5 etapas), lo que posiciona Research como contenedor del proceso.
- **WP-0013 / WP-0014:** **CAP-33 (Gestión de proyectos/casos de investigación)** es el **contenedor** que "contiene CAP-04…CAP-29"; sostiene todo el ciclo.
- **WP-0009:** los conceptos **Investigation** (proceso) y **Case** (asunto/contenedor) son unidades naturales de la investigación.
- **WP-0012:** las capacidades de producción están organizadas como un proceso de investigación→producción.

Lectura: Research es el **eje del proceso** y el contenedor natural del trabajo de un proyecto.

---

## 3. Evidencias a favor de **Knowledge Base** como núcleo

- **ARCH-0002 AP-001 (Knowledge First):** el conocimiento es "the primary product".
- **ARCH-0002 §2 (Problem Statement):** el problema primario es "the absence of a persistent and reusable knowledge system"; "lessons learned rarely survive beyond the completion of a single project".
- **ARCH-0002 §3:** la plataforma existe para "transform isolated research efforts into a continuously improving body of reusable knowledge assets".
- **ARCH-0002 §4 (Core Domain Vision):** el conocimiento reutilizable "constitutes the long-term value of DocumentaryAI".
- **ARCH-0002 §6 (Continuous Learning) y §9:** el éxito incluye "reusable knowledge is produced" y "that knowledge can improve subsequent research".
- **AP-003 (Evidence Before Knowledge) y AP-004 (Traceability):** el conocimiento se sustenta en evidencia con procedencia.
- **WP-0016 (Knowledge Asset Inventory):** identifica los **activos reutilizables** (conocimiento, procedencia, lecciones, assets) con reutilización **entre proyectos**.
- **WP-0011:** **Procedencia** y **Conocimiento** son los conceptos de **consenso más alto**.

Lectura: Knowledge Base es el **producto persistente** y la **fuente de valor a largo plazo** que sobrevive a cada proyecto.

---

## 4. Capacidades que pertenecen naturalmente a cada candidato

> Asignación **observada** (de WP-0013/0014), no normativa.

**Research (por-proyecto):**
- Ciclo completo del proyecto: **CAP-01…CAP-29** (ideación → aprendizaje).
- Contenedor: **CAP-33** (contiene CAP-04…CAP-29).
- Especialmente: investigación (CAP-04–CAP-10), narrativa (CAP-11–CAP-15), producción/publicación (CAP-16–CAP-25), post-publicación (CAP-26–CAP-29).

**Knowledge Base (transversal/persistente):**
- Sustrato transversal: **CAP-30 (Procedencia)**, **CAP-31 (Afirmaciones/evidencia)**, **CAP-32 (Incertidumbre/confianza)**.
- Producción y reutilización de conocimiento: **CAP-10 (Construcción de conocimiento)** y **CAP-29 (Aprendizaje)** (cuyo output realimenta CAP-01).

> Solape observado: **CAP-10**, **CAP-29** y las transversales **CAP-30/31/32** son **frontera** entre ambos candidatos (se generan dentro de un Research pero alimentan la Knowledge Base).

---

## 5. Activos de conocimiento asociados

> De WP-0016 / WP-0017 / WP-0019.

**Research (working set por-proyecto):** Lista de fuentes, Notas/material, Observación, Afirmación, Hecho, Hallazgo, Cronología, Contradicción, Hipótesis, Conclusión, Guion, Storyboard, Recursos, Vídeo final, Métricas.

**Knowledge Base (reutilizable entre proyectos):** Conocimiento, Procedencia, Evidencia (validada), Patrones, Lecciones aprendidas, "reusable structures" y "domain understanding" (lista de ARCH-0002 §6).

> Activos **compartidos/frontera:** Evidencia, Procedencia, Conocimiento — nacen en el Research y constituyen el valor de la Knowledge Base (WP-0016 marca su reutilización).

---

## 6. Riesgos observados para cada alternativa

> Riesgos **derivados de la documentación**, no juicios nuevos.

**Si el núcleo fuera Research:**
- Riesgo de **re-silado del conocimiento**: ARCH-0002 §2 identifica como problema que "lessons rarely survive beyond a single project"; un núcleo por-proyecto podría dejar la reutilización entre proyectos en segundo plano, contradiciendo AP-001/§4/§6.
- Riesgo de tratar el conocimiento como **subproducto** del proyecto, frente a AP-001 (Knowledge First).

**Si el núcleo fuera Knowledge Base:**
- Riesgo de **desligar el conocimiento de su proceso y procedencia** de origen, en tensión con AP-004 (Traceability) y AP-003 (Evidence Before Knowledge).
- Riesgo de **infraponderar AP-002** (Research Centric), donde la investigación es la actividad fundamental.
- Riesgo de derivar hacia un **"knowledge graph"/almacén**, que **ARCH-0002 §8** declara explícitamente que la plataforma **no es**.

---

## 7. Dependencias funcionales afectadas

> De WP-0014 (dependencias) y WP-0018 (ciclo).

- **Contenedor:** **CAP-33** contiene CAP-04…CAP-29. Si Research es núcleo, este contenedor es el centro; si lo es Knowledge Base, hay que situar la persistencia del conocimiento respecto a ese contenedor.
- **Sustrato transversal:** **CAP-30/31/32** son prerrequisito de CAP-08/09/10/13 (WP-0014). Son el material que la Knowledge Base acumularía y que el Research consume/produce.
- **Bucle de aprendizaje (frontera):** **CAP-29 → CAP-01** (WP-0014 §8) conecta el cierre de un Research con la mejora del siguiente: es exactamente el **punto de unión** entre ambos candidatos.
- **Procedencia (AP-004):** atraviesa investigación y narrativa (WP-0019 §6); cualquiera que sea el núcleo, la trazabilidad evidencia→conocimiento debe preservarse.

Observación: las dependencias **no** privilegian unívocamente a uno; el **bucle de aprendizaje** y las **transversales** son compartidos por ambos.

---

## 8. Tabla comparativa

| Dimensión | **Research** | **Knowledge Base** |
|---|---|---|
| Naturaleza | Proceso / contenedor por-proyecto | Producto acumulado / persistente entre proyectos |
| Soporte en ARCH-0002 | AP-002; §3; §9 (criterio 1) | AP-001; §2; §3; §4; §6; §9 (criterios 3–4) |
| Capacidades núcleo | CAP-01…CAP-29 + CAP-33 (contenedor) | CAP-10, CAP-29, CAP-30/31/32 |
| Activos asociados | Working set del proyecto (fuentes…vídeo, métricas) | Conocimiento, Procedencia, Evidencia validada, Patrones, Lecciones |
| Persistencia | Por proyecto | Transversal / a largo plazo |
| Aporta sobre todo | Ejecución del proceso completo | Valor reutilizable a largo plazo |
| Riesgo principal | Re-silado del conocimiento (vs AP-001/§2) | Pérdida de procedencia / "knowledge graph" (vs AP-004/§8) |
| Dependencias clave | CAP-33 contiene CAP-04…29 | CAP-30/31/32 sustrato; CAP-10/CAP-29 |
| Punto de unión | \<— bucle de aprendizaje CAP-29→CAP-01 —\> | (compartido) |

---

## 9. Observaciones (descriptivas)

- **ARCH-0002 respalda con fuerza a ambos** (AP-001 y AP-002 conviven), lo que explica que sean **candidatos** y no una elección obvia. Es una constatación, **no** una decisión.
- Los **puntos de frontera** (CAP-10, CAP-29, CAP-30/31/32 y el bucle CAP-29→CAP-01) son compartidos: la relación Research↔Knowledge Base parece **estrecha**, no excluyente.
- Las **restricciones de ARCH-0002 §8** (no knowledge graph) y **AP-004** (traceability) acotan los riesgos de la opción Knowledge Base; el **problema §2** (silos) acota los de la opción Research.
- Todo deriva de ARCH-0002 y WP-0007…WP-0019; **no** se ha elegido ganador, propuesto arquitectura ni definido agregados.

---

## 10. Referencias cruzadas

- ARCH-0002 · `docs/architecture/ARCH-0002-Domain-Philosophy.md`
- WP-0007 · `docs/architecture/Evidence-Centric-Domain-Research.md`
- WP-0009 · `docs/research/DOMAIN-ONTOLOGY-RESEARCH.md`
- WP-0011 · `docs/research/DOMAIN-EVIDENCE-SYNTHESIS-MATRIX.md`
- WP-0013 · `docs/research/MVP-CAPABILITY-INVENTORY.md`
- WP-0014 · `docs/research/CAPABILITY-DEPENDENCY-MAP.md`
- WP-0016 · `docs/research/KNOWLEDGE-ASSET-INVENTORY.md`
- WP-0017 · `docs/research/MVP-CAPABILITY-TRACEABILITY-MATRIX.md`
- WP-0018 · `docs/research/RESEARCH-LIFECYCLE-EXTRACTION.md`
- WP-0019 · `docs/research/DISCOVERY-TO-DOMAIN-MAPPING.md`

---

_Fin del análisis. Documento exclusivamente recopilatorio: no elige ganador, no propone arquitectura, no define agregados y no modifica documentos. Insumo para la decisión del Principal Architect sobre el núcleo del dominio._
