# RESEARCH LIFECYCLE TRACEABILITY — DocumentaryAI (DS-0004)

| Campo | Valor |
|---|---|
| **Document ID** | RES-RESEARCH-LIFECYCLE-TRACEABILITY |
| **Title** | Research Lifecycle Traceability — DocumentaryAI |
| **Status** | Draft (traceability) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | ARCH-0002; WP-0013, WP-0014, WP-0017, WP-0018, WP-0021, WP-0022 |

> **Documento de trazabilidad, exclusivamente recopilatorio.** Reúne toda la evidencia del **primer vertical (Research Lifecycle)** a partir de las fuentes citadas.
> **No** introduce conceptos nuevos, **no** diseña el dominio, **no** define comandos, **no** propone arquitectura y **no** modifica documentos. Deriva únicamente de ARCH-0002 y WP-0013/0014/0017/0018/0021/0022.

---

## 0. Alcance (interpretación)

"Primer vertical (Research Lifecycle)" se interpreta como la **Etapa 1 — Investigación** del ciclo de vida de **WP-0018** (**CAP-01…CAP-10**) más el **sustrato transversal** que la sostiene: **CAP-30** (Procedencia), **CAP-31** (Afirmaciones/evidencia), **CAP-32** (Incertidumbre/confianza) y el contenedor **CAP-33** (Proyecto/caso).

Es la franja que transforma fuentes en **base de conocimiento** (progresión Source → Evidence → Knowledge de ARCH-0002 §5). Las etapas posteriores (Narrativa, Producción, Publicación, Aprendizaje) quedan fuera de este vertical. *(Si el Principal Architect se refería a las 5 etapas completas, este documento se amplía.)*

---

## 1. Capacidades implicadas

| CAP | Nombre (WP-0013) | Rol en el vertical |
|---|---|---|
| CAP-01 | Ideación | Entrada del ciclo (realimentada por CAP-29) |
| CAP-02 | Selección de tema | Define el foco del proyecto |
| CAP-03 | Definición de objetivos | Fija metas de la investigación |
| CAP-04 | Planificación de investigación | Preguntas y plan |
| CAP-05 | Descubrimiento de fuentes | Localiza fuentes |
| CAP-06 | Recolección | Origen de materiales y del sustrato de evidencia |
| CAP-07 | Organización | Estructura el material |
| CAP-08 | Verificación | Núcleo de credibilidad |
| CAP-09 | Análisis | Cronologías, contradicciones, relaciones, hallazgos |
| CAP-10 | Construcción de conocimiento | Cierre: hipótesis, conclusiones, base de conocimiento |
| CAP-30 | Gestión de procedencia | Transversal (trazabilidad) |
| CAP-31 | Gestión de afirmaciones/evidencia | Transversal (sustrato de evidencia) |
| CAP-32 | Gestión de incertidumbre/confianza | Transversal (califica afirmaciones/conclusiones) |
| CAP-33 | Gestión de proyectos/casos | Contenedor del vertical |

---

## 2. Activos de conocimiento implicados

> De WP-0017 / WP-0022 (artefactos de WP-0013).

- **Entrada/realimentación:** Lecciones aprendidas, Métricas, Criterios.
- **Investigación:** Preguntas, Lista de fuentes, Metadatos, Notas/material, Observación.
- **Sustrato de evidencia:** Afirmación, Evidencia, Procedencia, Confianza/incertidumbre, Relación.
- **Análisis:** Hallazgo, Cronología, Contradicción.
- **Conocimiento:** Hecho, Hipótesis, Conclusión, Conocimiento.

> Salida del vertical: **base de conocimiento** (Hipótesis, Conclusión, Conocimiento, con Evidencia, Procedencia y Confianza), que alimenta la etapa de Narrativa (frontera con CAP-11).

---

## 3. Invariantes relacionadas

> De WP-0021 (vía WP-0022). Universales (aplican a todo el vertical): **INV-002, INV-017** (Research Centric), **INV-009, INV-019** (AI Independence), **INV-010** (Capability Independence), **INV-026** (prerrequisitos funcionales).

Específicas por concentración:
- **Trazabilidad/Procedencia:** INV-004, INV-005, INV-007, INV-015, INV-020, INV-024.
- **Epistemológicas:** INV-003 (Evidence Before Knowledge), INV-008 (Knowledge ≠ documents), INV-021 (evidencia relacional), INV-022 (hecho↔interpretación), INV-023 (conocimiento revisable).
- **Calidad:** INV-006 (conocimiento explicable), INV-025 (incertidumbre explícita), INV-016 (conocimiento reutilizable preferido).
- **Otras:** INV-001 (Knowledge First, en CAP-10), INV-011 (automatización donde aumenta conocimiento).

---

## 4. Principios de ARCH-0002 aplicables

- **AP-002 — Research Centric:** todo el vertical es la actividad de investigación (todas las capacidades; CAP-33 contenedor).
- **AP-003 — Evidence Before Knowledge:** CAP-06, CAP-08, CAP-10, CAP-31.
- **AP-004 — Traceability by Design:** CAP-06, CAP-08, CAP-13(frontera), CAP-30 (y §5 "preserving traceability").
- **AP-001 — Knowledge First:** CAP-10 (producción de conocimiento como producto primario).
- **AP-005 — AI Independence:** transversal (los conceptos del vertical son independientes del proveedor de IA).
- **AP-006 — Capability Independence:** todas (las capacidades perduran; sus implementaciones, no).
- **§5 — Nature of Knowledge:** progresión Source → Evidence → Knowledge es exactamente este vertical; "every assertion … traceable back to supporting evidence".

---

## 5. Flujo del ciclo de vida (vertical Research)

> Sub-flujo de WP-0018 (Etapa 1 + transversales). Solo dependencias documentadas; no es arquitectura.

```
[ CAP-33 Proyecto/caso : contiene el vertical ]

CAP-01 → CAP-02 → CAP-03 → CAP-04 → CAP-05 → CAP-06 → CAP-07 → CAP-08 → CAP-09 → CAP-10
                                          │
   transversales:  CAP-30 (Procedencia) y CAP-31 (Afirmaciones/evidencia) nacen en CAP-06
                   CAP-32 (Incertidumbre) depende de CAP-31
                   CAP-30/31 usadas por CAP-08, CAP-09, CAP-10 ; CAP-32 por CAP-08, CAP-10
                                          │
                                          ▼
                       salida: BASE DE CONOCIMIENTO  →  (CAP-11, etapa Narrativa)

   realimentación: CAP-29 (Aprendizaje, fuera del vertical) → CAP-01
```

---

## 6. Dependencias funcionales

> De WP-0014 (acotadas al vertical).

| CAP | Depende de | Habilita (dentro del vertical) |
|---|---|---|
| CAP-01 | — (realim. CAP-29) | CAP-02 |
| CAP-02 | CAP-01 | CAP-03, CAP-33 |
| CAP-03 | CAP-02 | CAP-04 |
| CAP-04 | CAP-03 | CAP-05 |
| CAP-05 | CAP-04 | CAP-06 |
| CAP-06 | CAP-05, CAP-30 | CAP-07, CAP-30, CAP-31 |
| CAP-07 | CAP-06 | CAP-08 |
| CAP-08 | CAP-07, CAP-31, CAP-32 | CAP-09 |
| CAP-09 | CAP-08, CAP-30, CAP-31 | CAP-10 |
| CAP-10 | CAP-09, CAP-30, CAP-31, CAP-32 | CAP-11 (frontera, fuera del vertical) |
| CAP-30 | CAP-06 | CAP-08, CAP-09, CAP-10 |
| CAP-31 | CAP-06 | CAP-08, CAP-09, CAP-10 |
| CAP-32 | CAP-31 | CAP-08, CAP-10 |
| CAP-33 | CAP-02 | contiene CAP-04…CAP-10 (y resto del ciclo) |

Prerrequisitos críticos del vertical: **CAP-33** (contenedor), **CAP-06** (origen de materiales/evidencia), **CAP-30/31** (sustrato de procedencia/evidencia).

---

## 7. Matriz de trazabilidad completa

> Acción = verbo observable (WP-0022), **no** comando. Activos de WP-0017/0022. Invariantes de WP-0021. Principios de ARCH-0002.

| CAP | Acción observable | Activos usados | Activos producidos | Invariantes | Principios ARCH-0002 | Depende de |
|---|---|---|---|---|---|---|
| CAP-01 | Idear | Lecciones aprendidas | (no inventariado: banco de ideas) | INV-011 | AP-002 | — |
| CAP-02 | Seleccionar tema | Métricas, Criterios | (no inventariado: ficha de tema) | (univ.) | AP-002 | CAP-01 |
| CAP-03 | Definir objetivos | — | (no inventariado: objetivos) | (univ.) | AP-002 | CAP-02 |
| CAP-04 | Planificar investigación | — | Preguntas | (univ.) | AP-002 | CAP-03 |
| CAP-05 | Descubrir fuentes | — | Lista de fuentes, Metadatos | INV-011 | AP-002 | CAP-04 |
| CAP-06 | Recolectar | Lista de fuentes | Notas/material, Observación, Afirmación, Evidencia, Procedencia | INV-003, INV-004, INV-007, INV-008, INV-011, INV-020 | AP-002, AP-003, AP-004 | CAP-05, CAP-30 |
| CAP-07 | Organizar | Notas/material | Notas/material, Metadatos | INV-008, INV-011 | AP-002 | CAP-06 |
| CAP-08 | Verificar | Afirmación, Evidencia, Procedencia, Confianza | Hecho, Confianza | INV-003, INV-005, INV-007, INV-020, INV-021, INV-022 | AP-002, AP-003, AP-004 | CAP-07, CAP-31, CAP-32 |
| CAP-09 | Analizar | Evidencia, Procedencia | Hallazgo, Cronología, Contradicción, Relación | INV-007, INV-020, INV-022 | AP-002, AP-004 | CAP-08, CAP-30, CAP-31 |
| CAP-10 | Consolidar conocimiento | Hallazgo | Hipótesis, Conclusión, Conocimiento, Confianza, Preguntas | INV-001, INV-003, INV-006, INV-007, INV-016, INV-020, INV-023 | AP-001, AP-002, AP-003 | CAP-09, CAP-30, CAP-31, CAP-32 |
| CAP-30 | Registrar procedencia | Materiales, Afirmación | Procedencia | INV-004, INV-015, INV-020, INV-024 | AP-004 | CAP-06 |
| CAP-31 | Gestionar afirmaciones/evidencia | Observación, Notas/material | Afirmación, Evidencia, Relación | INV-003, INV-005, INV-021 | AP-003, AP-004 | CAP-06 |
| CAP-32 | Calificar incertidumbre | Afirmación, Source | Confianza/incertidumbre | INV-025 | AP-003 | CAP-31 |
| CAP-33 | Contener proyecto | (no inventariado: ficha, objetivos) | (no inventariado: contenedor) | INV-002, INV-017 | AP-002 | CAP-02 |

> (univ.) = solo bajo invariantes universales (INV-002/009/010/017/019/026). Principios universales adicionales aplicables a todas las filas: AP-005, AP-006, AP-009-equivalente (AI independence).

---

## 8. Observaciones (descriptivas)

- El vertical concentra el **sustrato epistémico y de trazabilidad** del sistema: las invariantes de Procedencia/Trazabilidad (INV-004/005/007/020/024) y las epistemológicas (INV-003/008/021/022/023) caen casi todas aquí.
- Los **prerrequisitos críticos** (CAP-33, CAP-06, CAP-30/31) coinciden con los señalados en WP-0014; son los nodos de los que depende el resto del vertical.
- La **salida** del vertical (base de conocimiento) es el activo bisagra hacia la Narrativa (WP-0018), y el material que la Knowledge Base acumularía (WP-0020, sin decidir aquí).
- Todo deriva de las fuentes citadas; **no** se ha introducido concepto, comando, arquitectura ni decisión.

---

## 9. Referencias cruzadas

- ARCH-0002 · `docs/architecture/ARCH-0002-Domain-Philosophy.md`
- WP-0013 · `docs/research/MVP-CAPABILITY-INVENTORY.md`
- WP-0014 · `docs/research/CAPABILITY-DEPENDENCY-MAP.md`
- WP-0017 · `docs/research/MVP-CAPABILITY-TRACEABILITY-MATRIX.md`
- WP-0018 · `docs/research/RESEARCH-LIFECYCLE-EXTRACTION.md`
- WP-0021 · `docs/research/DOMAIN-INVARIANT-EXTRACTION.md`
- WP-0022 · `docs/research/CAPABILITY-COMMAND-MAPPING.md`

---

_Fin de la trazabilidad. Documento exclusivamente recopilatorio del primer vertical (Research Lifecycle): no introduce conceptos nuevos, no diseña el dominio, no define comandos, no propone arquitectura y no modifica documentos existentes._
