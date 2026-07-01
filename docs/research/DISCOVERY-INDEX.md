# DISCOVERY INDEX — DocumentaryAI (WP-0015)

| Campo | Valor |
|---|---|
| **Document ID** | RES-DISCOVERY-INDEX |
| **Title** | Discovery Consolidation Index — DocumentaryAI |
| **Status** | Draft (index) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | Ver §10 (referencias cruzadas) |

> **Documento índice.** Consolida la fase Discovery (WP-0007 a WP-0014) para facilitar su consulta durante el diseño arquitectónico.
> **No** genera conocimiento nuevo, **no** interpreta resultados, **no** realiza síntesis arquitectónicas, **no** propone arquitectura y **no** modifica ningún documento existente. Todo se deriva exclusivamente de los documentos ya creados.

---

## 1. Resumen de la fase Discovery

La fase Discovery agrupó el trabajo de investigación previo al diseño del MVP. Comprendió dos bloques:

- **Domain Discovery (Sprint A-01):** investigación del dominio (qué es la evidencia, terminología, patrones epistémicos) y su síntesis.
- **MVP Definition (Sprint A-02):** mapeo del proceso de producción para YouTube, inventario de capacidades del MVP y mapa de dependencias.

El resultado es un cuerpo de **evidencia documental** (no decisiones) que sirve de base para los entregables del Principal Architect (p. ej. ARCH-0002 — Domain Philosophy y ARCH-0003 — MVP Capability Architecture). Esta consolidación **no** añade conclusiones nuevas: solo organiza y referencia lo producido.

> Nota: en el rango WP-0007…WP-0014 se intercala **WP-0008**, que es un trabajo de **gobernanza** (incorporación del PROJECT-CHARTER), no de Discovery. Se lista por completitud de la cronología, marcado como gobernanza.

---

## 2. Cronología (WP-0007 → WP-0014)

| Orden | WP | Título | Bloque |
|---|---|---|---|
| 1 | **WP-0007** | Evidence-Centric Domain Research | Domain Discovery (A-01) |
| 2 | *WP-0008* | *Project Charter (incorporación)* | *Gobernanza (no Discovery)* |
| 3 | **WP-0009** | Domain Ontology Research | Domain Discovery (A-01) |
| 4 | **WP-0010** | Epistemic Domain Pattern Research | Domain Discovery (A-01) |
| 5 | **WP-0011** | Domain Evidence Synthesis Matrix | Domain Discovery (A-01) |
| 6 | **WP-0012** | YouTube Documentary Production Capability Map | MVP Definition (A-02) |
| 7 | **WP-0013** | MVP Capability Inventory | MVP Definition (A-02) |
| 8 | **WP-0014** | Capability Dependency Map | MVP Definition (A-02) |

---

## 3. Objetivo de cada Work Package

- **WP-0007 — Evidence-Centric Domain Research:** investigar enfoques para modelar plataformas centradas en evidencia y conocimiento (document/case/evidence/knowledge-centric) y los riesgos de tratar la evidencia como objeto fundamental. Material de apoyo, sin diseño.
- **WP-0008 — Project Charter (gobernanza):** incorporar el documento oficial de gobernanza (roles, jerarquía de decisiones y documentación, metodología). No pertenece a Discovery; se cita por estar en la cronología.
- **WP-0009 — Domain Ontology Research:** recopilar definiciones, variantes, ambigüedades y diferencias entre disciplinas de 24 conceptos del dominio, como base terminológica. Sin modelar.
- **WP-0010 — Epistemic Domain Pattern Research:** documentar cómo nueve disciplinas construyen conocimiento (observación→evidencia→razonamiento→conclusión) y comparar ejes transversales. Descriptivo.
- **WP-0011 — Domain Evidence Synthesis Matrix:** sintetizar WP-0007/0009/0010 en una matriz de trazabilidad por tema (consenso/divergencias). Sin fuentes nuevas.
- **WP-0012 — YouTube Documentary Production Capability Map:** describir el proceso completo de producción de un documental para YouTube como capacidades, de la idea al aprendizaje. Descriptivo.
- **WP-0013 — MVP Capability Inventory:** consolidar la evidencia en un inventario de capacidades del MVP, clasificarlas funcionalmente e identificar dependencias. Síntesis, sin diseño.
- **WP-0014 — Capability Dependency Map:** derivar de WP-0013 el mapa de dependencias funcionales (habilitadoras, consumidoras, transversales, ciclos, independientes). Sin diseño.

---

## 4. Principales entregables por WP

| WP | Entregable(s) principal(es) |
|---|---|
| WP-0007 | Investigación de enfoques "centric" + riesgos de Evidence como Aggregate Root |
| WP-0008 | PROJECT-CHARTER (gobernanza) |
| WP-0009 | Inventario de 24 conceptos con definiciones/variantes/ambigüedades; preguntas abiertas |
| WP-0010 | Patrones epistémicos de 9 disciplinas + comparativa de 8 ejes |
| WP-0011 | Matriz de trazabilidad por tema (consenso/divergencias/vacíos) |
| WP-0012 | Mapa de 29 capacidades de producción + artefactos + oportunidades |
| WP-0013 | Inventario de 33 capacidades del MVP + clasificación funcional (21/10/2) |
| WP-0014 | Mapa de dependencias funcionales (transversales, habilitadoras, consumidoras, ciclos) |

---

## 5. Dependencias entre documentos

> Qué documento se apoya en cuál (declarado en cada documento).

```
WP-0007 ─┐
WP-0009 ─┼─► WP-0011 (síntesis de 0007+0009+0010)
WP-0010 ─┘

WP-0011 ─┐
WP-0012 ─┴─► WP-0013 (inventario, usa síntesis + mapa de producción)

WP-0013 ──► WP-0014 (mapa de dependencias, deriva solo de 0013)

WP-0008 (gobernanza) — independiente del flujo Discovery
```

Resumen:
- **WP-0011** depende de WP-0007, WP-0009 y WP-0010.
- **WP-0013** depende de WP-0007, WP-0009, WP-0010, WP-0011 y WP-0012.
- **WP-0014** depende exclusivamente de WP-0013.
- **WP-0008** no participa en la cadena Discovery.

---

## 6. Orden recomendado de lectura (nuevo arquitecto)

1. **WP-0007** — encuadre del problema (enfoques centric, riesgos de la evidencia como objeto fundamental).
2. **WP-0009** — vocabulario del dominio (24 conceptos).
3. **WP-0010** — patrones de construcción de conocimiento por disciplina.
4. **WP-0011** — síntesis comparada de los tres anteriores (consensos/divergencias).
5. **WP-0012** — proceso de producción para YouTube (capacidades del flujo real).
6. **WP-0013** — inventario de capacidades del MVP y su clasificación funcional.
7. **WP-0014** — mapa de dependencias entre esas capacidades.
- *(Opcional, contexto)* **WP-0008** — PROJECT-CHARTER (gobernanza), si se necesita el marco de roles/metodología.

---

## 7. Tabla de trazabilidad (WP → Documento generado)

| WP | Documento | Ruta |
|---|---|---|
| WP-0007 | Evidence-Centric Domain Research | `docs/architecture/Evidence-Centric-Domain-Research.md` |
| WP-0008 | Project Charter *(gobernanza)* | `docs/governance/PROJECT-CHARTER.md` |
| WP-0009 | Domain Ontology Research | `docs/research/DOMAIN-ONTOLOGY-RESEARCH.md` |
| WP-0010 | Epistemic Domain Pattern Research | `docs/research/EPISTEMIC-DOMAIN-PATTERN-RESEARCH.md` |
| WP-0011 | Domain Evidence Synthesis Matrix | `docs/research/DOMAIN-EVIDENCE-SYNTHESIS-MATRIX.md` |
| WP-0012 | YouTube Documentary Production Capability Map | `docs/research/YOUTUBE-DOCUMENTARY-PRODUCTION-CAPABILITY-MAP.md` |
| WP-0013 | MVP Capability Inventory | `docs/research/MVP-CAPABILITY-INVENTORY.md` |
| WP-0014 | Capability Dependency Map | `docs/research/CAPABILITY-DEPENDENCY-MAP.md` |
| WP-0015 | Discovery Index *(este documento)* | `docs/research/DISCOVERY-INDEX.md` |

---

## 8. Glosario mínimo

> Términos usados durante Discovery. Definiciones **tomadas de los documentos existentes** (principalmente WP-0009); no se introducen conceptos nuevos. Versión abreviada; el detalle vive en cada documento fuente.

- **Evidence (Evidencia):** información o material que tiende a apoyar o refutar una afirmación/hipótesis; tratada como **rol relacional** (WP-0007/0009/0010/0011).
- **Observation (Observación):** constatación directa de un hecho previa a su interpretación (WP-0009).
- **Source (Fuente):** origen del que procede información/material (WP-0009).
- **Document (Documento):** unidad de contenido registrada; contenedor/portador (WP-0009).
- **Claim (Afirmación):** enunciado propuesto como verdadero, sujeto a respaldo (WP-0009).
- **Fact (Hecho):** afirmación tenida por verdadera/verificable; umbral variable por disciplina (WP-0009/0010).
- **Finding (Hallazgo):** resultado de un análisis (WP-0009).
- **Hypothesis (Hipótesis):** explicación tentativa contrastable (WP-0009/0010).
- **Conclusion (Conclusión):** afirmación final derivada del razonamiento (WP-0009).
- **Knowledge (Conocimiento):** información estructurada, contextualizada y justificada (WP-0009; DIKW).
- **Provenance (Procedencia):** registro del origen e historia de algo (WP-0009; consenso alto en WP-0011).
- **Interpretation (Interpretación):** valoración mutable frente al hecho constatado (separación hecho↔interpretación; WP-0007/0010/0011).
- **Capability (Capacidad):** algo que el proceso/sistema debe poder hacer (WP-0012/0013).
- **Artifact (Artefacto):** producto generado por una capacidad (WP-0012).
- **Transversal / Enabling / Consumer capability:** capacidad que atraviesa grupos / habilita a muchas / depende de varias (WP-0014).
- **Ubiquitous Language:** lenguaje propio del proyecto a definir por el Architect (referido en AC-0003; registrado en el índice de arquitectura).

---

## 9. Estado final de la fase

- **Domain Discovery (Sprint A-01):** **Cerrado.** (WP-0007, WP-0009, WP-0010, WP-0011; investigación documental y terminológica declaradas completas en el cierre de WP-0009.)
- **MVP Definition (Sprint A-02) — investigación:** WP-0012, WP-0013 y WP-0014 **completados**.
- **Esta consolidación (WP-0015):** la fase Discovery queda **cerrada** a efectos de consulta; este índice es su punto de entrada.
- **Siguiente:** entregables de diseño a cargo del Principal Architect (p. ej. ARCH-0002 — Domain Philosophy y ARCH-0003 — MVP Capability Architecture). **No** forman parte de esta consolidación.

> Observación de registro (no es modificación): el cierre formal y la incorporación a «Evidencia arquitectónica» de WP-0010…WP-0014 dependen de instrucción del Principal Architect; solo WP-0009 tiene cierre registrado hasta la fecha.

---

## 10. Referencias cruzadas

- WP-0007 · `docs/architecture/Evidence-Centric-Domain-Research.md`
- WP-0008 · `docs/governance/PROJECT-CHARTER.md` *(gobernanza)*
- WP-0009 · `docs/research/DOMAIN-ONTOLOGY-RESEARCH.md`
- WP-0010 · `docs/research/EPISTEMIC-DOMAIN-PATTERN-RESEARCH.md`
- WP-0011 · `docs/research/DOMAIN-EVIDENCE-SYNTHESIS-MATRIX.md`
- WP-0012 · `docs/research/YOUTUBE-DOCUMENTARY-PRODUCTION-CAPABILITY-MAP.md`
- WP-0013 · `docs/research/MVP-CAPABILITY-INVENTORY.md`
- WP-0014 · `docs/research/CAPABILITY-DEPENDENCY-MAP.md`
- WP-0015 · `docs/research/DISCOVERY-INDEX.md` *(este documento)*
- Contexto de arquitectura · `docs/architecture/Architecture-Index.md`

---

_Fin del índice de consolidación. Documento exclusivamente organizativo: deriva de los documentos existentes, no genera conocimiento ni síntesis arquitectónica, no introduce conceptos nuevos, no propone arquitectura, no modifica los WP y no crea RFC/ADR/ARCH/SPEC._
