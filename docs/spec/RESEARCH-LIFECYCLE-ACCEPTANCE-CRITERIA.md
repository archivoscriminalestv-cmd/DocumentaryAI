# RESEARCH LIFECYCLE — ACCEPTANCE CRITERIA (DS-0006)

| Campo | Valor |
|---|---|
| **Document ID** | SPEC-RL-ACCEPTANCE-CRITERIA |
| **Title** | Research Lifecycle — Acceptance Criteria |
| **Status** | Draft (extraction) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | ARCH-0002; WP-0013, WP-0016, WP-0017, WP-0018, WP-0021; DS-0004; SPEC-0001 |

> **Documento de extracción, exclusivamente recopilatorio.** Extrae los **criterios de aceptación verificables** del primer vertical (Research Lifecycle) ya presentes en la documentación normativa.
> **No** crea criterios nuevos, **no** reformula el significado de las fuentes, **no** define tests, **no** diseña implementación y **no** define comandos.
> **Fuente única de criterios:** los **Success Criteria** de **ARCH-0002 §9** (los únicos criterios de aceptación/éxito explícitos en la documentación normativa). Las invariantes (WP-0021) se citan como **condiciones relacionadas**, no como criterios nuevos.

---

## 1. Alcance

Vertical: **Research Lifecycle** según DS-0004 (CAP-01…CAP-10 + sustrato transversal CAP-30/31/32/33). Los criterios se extraen de ARCH-0002 §9 y se relacionan con las capacidades e invariantes de ese vertical. Donde un criterio implica capacidades **fuera** del vertical (p. ej. el bucle de aprendizaje), se señala.

---

## 2. Criterios de aceptación extraídos

### AC-RL-01 — Un proceso de investigación completo puede ejecutarse
- **Descripción verificable (verbatim):** "a complete research process can be executed".
- **Fuente documental:** ARCH-0002 §9 (criterio 1); flujo en WP-0018; capacidades en WP-0013.
- **Capacidades relacionadas:** CAP-01…CAP-10, contenedor CAP-33.
- **Invariantes relacionadas:** INV-002, INV-017 (Research Centric).
- **Resultado esperado:** un proyecto de investigación puede recorrer el vertical de principio a fin (de la ideación a la base de conocimiento).
- **Evidencia necesaria para verificarlo:** existencia de un proyecto/caso (CAP-33) con sus activos generados a lo largo del flujo (Lista de fuentes, Notas/material, Evidencia, …, Conocimiento), conforme a WP-0016/WP-0017.

### AC-RL-02 — La evidencia permanece trazable a lo largo del proceso
- **Descripción verificable (verbatim):** "evidence remains traceable throughout the process".
- **Fuente documental:** ARCH-0002 §9 (criterio 2); AP-004 (§7); §5.
- **Capacidades relacionadas:** CAP-06, CAP-08, CAP-09, CAP-10, CAP-30.
- **Invariantes relacionadas:** INV-004, INV-005, INV-007, INV-015, INV-020, INV-024.
- **Resultado esperado:** toda afirmación/conocimiento puede rastrearse hasta la evidencia y la fuente que lo sustentan, en todas las etapas del vertical.
- **Evidencia necesaria para verificarlo:** registros de **Procedencia** (CAP-30) que vinculan afirmaciones↔evidencia↔fuente; trazas conservadas entre etapas (§5 "preserving traceability"), conforme a WP-0016/WP-0017.

### AC-RL-03 — Se produce conocimiento reutilizable
- **Descripción verificable (verbatim):** "reusable knowledge is produced".
- **Fuente documental:** ARCH-0002 §9 (criterio 3); AP-001 (§7); §4; §6.
- **Capacidades relacionadas:** CAP-10 (con sustrato CAP-30/31/32).
- **Invariantes relacionadas:** INV-001, INV-006, INV-016, INV-023.
- **Resultado esperado:** el vertical produce conocimiento (hipótesis, conclusiones, base de conocimiento) reutilizable y **explicable**.
- **Evidencia necesaria para verificarlo:** activo **Conocimiento** / base de conocimiento (WP-0016) con su procedencia (AC-RL-02) y su confianza asociada (CAP-32).

### AC-RL-04 — El conocimiento puede mejorar investigaciones posteriores
- **Descripción verificable (verbatim):** "that knowledge can improve subsequent research".
- **Fuente documental:** ARCH-0002 §9 (criterio 4); §6; AP-008 (§7).
- **Capacidades relacionadas:** CAP-29 (Aprendizaje) → CAP-01 (realimentación). *(Frontera: el bucle de aprendizaje está fuera del vertical; el conocimiento de CAP-10 es su insumo.)*
- **Invariantes relacionadas:** INV-012, INV-013, INV-016, INV-018.
- **Resultado esperado:** el conocimiento/las lecciones de un proyecto pueden reutilizarse para mejorar el siguiente.
- **Evidencia necesaria para verificarlo:** **Lecciones aprendidas** (WP-0016) reutilizadas como entrada de CAP-01/CAP-02 en un proyecto posterior.

### AC-RL-05 — El éxito se mide por aprendizaje acumulado, no por nº de funcionalidades
- **Descripción verificable (verbatim):** "Feature count is not a success metric. Accumulated learning is."
- **Fuente documental:** ARCH-0002 §9.
- **Capacidades relacionadas:** transversal (CAP-26 Métricas, CAP-29 Aprendizaje). *(Medición; parcialmente fuera del vertical.)*
- **Invariantes relacionadas:** INV-011, INV-016, INV-018.
- **Resultado esperado:** la valoración de éxito se basa en el crecimiento de conocimiento reutilizable, no en el recuento de funcionalidades.
- **Evidencia necesaria para verificarlo:** evidencia del crecimiento de activos reutilizables / lecciones aprendidas (WP-0016) a lo largo de proyectos.

---

## 3. Observaciones (descriptivas)

- Los **únicos** criterios de aceptación/éxito explícitos en la documentación normativa son los de **ARCH-0002 §9**; se han extraído los 4 numerados más el enunciado de métrica. **No** se han creado criterios nuevos.
- **AC-RL-01, AC-RL-02 y AC-RL-03** caen plenamente dentro del vertical Research Lifecycle; **AC-RL-04 y AC-RL-05** implican el bucle de aprendizaje/medición, **parcialmente fuera** del vertical (señalado).
- Las **invariantes** de WP-0021 aportan condiciones verificables adicionales, pero se citan como "relacionadas" para **no** promoverlas a criterios nuevos (restricción del WP).
- La "Evidencia necesaria" describe **artefactos/activos documentados** que demostrarían el criterio (de WP-0016/0017); **no** son tests ni procedimientos de implementación.
- Estos criterios son candidatos a poblar la sección **§12 Acceptance Criteria** de **SPEC-0001**, cuando esta se complete (pendiente de RFC-0002).

---

## 4. Referencias cruzadas

- ARCH-0002 · `docs/architecture/ARCH-0002-Domain-Philosophy.md`
- WP-0013 · `docs/research/MVP-CAPABILITY-INVENTORY.md`
- WP-0016 · `docs/research/KNOWLEDGE-ASSET-INVENTORY.md`
- WP-0017 · `docs/research/MVP-CAPABILITY-TRACEABILITY-MATRIX.md`
- WP-0018 · `docs/research/RESEARCH-LIFECYCLE-EXTRACTION.md`
- WP-0021 · `docs/research/DOMAIN-INVARIANT-EXTRACTION.md`
- DS-0004 · `docs/research/RESEARCH-LIFECYCLE-TRACEABILITY.md`
- SPEC-0001 · `docs/spec/SPEC-0001-Research-Lifecycle.md`

---

_Fin de la extracción. Documento exclusivamente recopilatorio: no crea criterios nuevos, no reformula el significado de las fuentes, no define tests, no diseña implementación y no define comandos._
