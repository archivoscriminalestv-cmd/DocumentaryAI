# MVP CAPABILITY TRACEABILITY MATRIX — DocumentaryAI (WP-0017)

| Campo | Valor |
|---|---|
| **Document ID** | RES-MVP-CAP-TRACEABILITY |
| **Title** | MVP Capability Traceability Matrix — DocumentaryAI |
| **Status** | Draft (synthesis) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | WP-0013, WP-0014, WP-0016 (ver §6) |

> **Documento de síntesis.** Matriz de trazabilidad entre las capacidades del MVP (WP-0013), sus dependencias (WP-0014) y los activos de conocimiento (WP-0016).
> **No** introduce relaciones nuevas, **no** infiere arquitectura, **no** propone componentes/entidades/modelos, **no** aplica DDD, **no** decide y **no** modifica documentos existentes.

---

## 1. Objetivo y método

Ofrecer una vista única que enlace cada capacidad del MVP con sus dependencias funcionales y con los activos de conocimiento con los que interactúa, para apoyo del Principal Architect.

**Método (sin relaciones nuevas):**
- **Dependencias:** tomadas literalmente de WP-0014 (columna "Depende de").
- **Activos con los que interactúa:** derivados de los artefactos **"utilizados / producidos"** que cada capacidad declara en WP-0013, **intersectados** con los tipos de activo inventariados en WP-0016.
- **Regla de prudencia:** cuando un artefacto declarado en WP-0013 **no** corresponde a un tipo de activo inventariado en WP-0016 (p. ej. "objetivos", "escaleta", "comentarios", "contenedor de proyecto"), **no** se fuerza ningún vínculo. Esas capacidades se listan aparte (§4).
- Etiquetas de activo abreviadas según los nombres de WP-0016.

---

## 2. Matriz de trazabilidad (una fila por capacidad)

| ID | Nombre | Dependencias (WP-0014) | Activos de conocimiento con los que interactúa (de WP-0013 ∩ WP-0016) | Documentos fuente |
|---|---|---|---|---|
| CAP-01 | Ideación | — (realim. CAP-29) | Lecciones aprendidas | WP-0013, WP-0014, WP-0012(C-01) |
| CAP-02 | Selección de tema | CAP-01 | Métricas, Criterios | WP-0013, WP-0014, WP-0012(C-02) |
| CAP-03 | Definición de objetivos | CAP-02 | *(sin activo inventariado — ver §4)* | WP-0013, WP-0014, WP-0012(C-03) |
| CAP-04 | Planificación de investigación | CAP-03 | Preguntas | WP-0013, WP-0014, WP-0012(C-04) |
| CAP-05 | Descubrimiento de fuentes | CAP-04 | Lista de fuentes, Metadatos | WP-0013, WP-0014, WP-0012(C-05), WP-0009 |
| CAP-06 | Recolección | CAP-05, CAP-30 | Notas/material, Observación, Afirmación, Evidencia, Procedencia | WP-0013, WP-0014, WP-0012(C-06) |
| CAP-07 | Organización | CAP-06 | Notas/material, Metadatos | WP-0013, WP-0014, WP-0012(C-07) |
| CAP-08 | Verificación | CAP-07, CAP-31, CAP-32 | Afirmación, Evidencia, Hecho, Confianza/incertidumbre, Procedencia | WP-0013, WP-0014, WP-0012(C-08), WP-0010, WP-0011 |
| CAP-09 | Análisis | CAP-08, CAP-30, CAP-31 | Hallazgo, Cronología, Contradicción, Relación, Evidencia, Procedencia | WP-0013, WP-0014, WP-0012(C-09), WP-0007, WP-0011 |
| CAP-10 | Construcción de conocimiento | CAP-09, CAP-30, CAP-31, CAP-32 | Hipótesis, Conclusión, Conocimiento, Confianza/incertidumbre, Preguntas, Procedencia | WP-0013, WP-0014, WP-0012(C-10), WP-0007/09/10/11 |
| CAP-11 | Diseño narrativo | CAP-10, CAP-03 | Conocimiento | WP-0013, WP-0014, WP-0012(C-11) |
| CAP-12 | Estructura | CAP-11 | *(sin activo inventariado — ver §4)* | WP-0013, WP-0014, WP-0012(C-12) |
| CAP-13 | Guion | CAP-12, CAP-30, CAP-31 | Guion, Conocimiento, Afirmación, Procedencia | WP-0013, WP-0014, WP-0012(C-13) |
| CAP-14 | Storyboard | CAP-13 | Guion, Storyboard | WP-0013, WP-0014, WP-0012(C-14) |
| CAP-15 | Planificación visual | CAP-14 | Storyboard | WP-0013, WP-0014, WP-0012(C-15) |
| CAP-16 | Producción de recursos | CAP-15, CAP-23 | Recursos (assets) | WP-0013, WP-0014, WP-0012(C-16) |
| CAP-17 | Locución | CAP-13 | Guion, Recursos (assets) | WP-0013, WP-0014, WP-0012(C-17) |
| CAP-18 | Edición | CAP-16, CAP-17, CAP-14 | Recursos (assets), Storyboard | WP-0013, WP-0014, WP-0012(C-18) |
| CAP-19 | Control de calidad | CAP-18, CAP-08 | Criterios | WP-0013, WP-0014, WP-0012(C-19) |
| CAP-20 | Exportación | CAP-19 | Vídeo final | WP-0013, WP-0014, WP-0012(C-20) |
| CAP-21 | Empaquetado | CAP-11, CAP-20 | Vídeo final | WP-0013, WP-0014, WP-0012(C-21) |
| CAP-22 | Metadatos / SEO | CAP-13, CAP-20 | Metadatos, Guion | WP-0013, WP-0014, WP-0012(C-22) |
| CAP-23 | Derechos y cumplimiento | CAP-05, CAP-16 | Recursos (assets), Lista de fuentes, Procedencia | WP-0013, WP-0014, WP-0012(C-23) |
| CAP-24 | Publicación | CAP-20, CAP-21, CAP-22, CAP-23 | Vídeo final, Metadatos | WP-0013, WP-0014, WP-0012(C-24) |
| CAP-25 | Distribución | CAP-24 | Vídeo final, Recursos (assets) | WP-0013, WP-0014, WP-0012(C-25) |
| CAP-26 | Métricas | CAP-24 | Métricas | WP-0013, WP-0014, WP-0012(C-26) |
| CAP-27 | Retroalimentación | CAP-26, CAP-28 | Métricas | WP-0013, WP-0014, WP-0012(C-27) |
| CAP-28 | Interacción con la comunidad | CAP-24 | *(sin activo inventariado — ver §4)* | WP-0013, WP-0014, WP-0012(C-28) |
| CAP-29 | Aprendizaje | CAP-27, CAP-28 | Lecciones aprendidas, Métricas | WP-0013, WP-0014, WP-0012(C-29) |
| CAP-30 | Gestión de procedencia | CAP-06 | Procedencia | WP-0013, WP-0014, WP-0007/09/10/11 |
| CAP-31 | Gestión de afirmaciones/evidencia | CAP-06 | Afirmación, Evidencia, Relación | WP-0013, WP-0014, WP-0007/09/10/11 |
| CAP-32 | Gestión de incertidumbre/confianza | CAP-31 | Confianza/incertidumbre | WP-0013, WP-0014, WP-0010, WP-0011 |
| CAP-33 | Gestión de proyectos/casos | CAP-02 | *(sin activo inventariado — ver §4)* | WP-0013, WP-0014, WP-0009 |

---

## 3. Tabla de cobertura (activo → capacidades relacionadas)

> Relación inversa de §2. Solo activos de WP-0016 que aparecen vinculados a alguna capacidad por la regla de §1.

| Activo (WP-0016) | Capacidades relacionadas |
|---|---|
| Evidencia | CAP-06, CAP-08, CAP-09, CAP-31 |
| Observación | CAP-06 |
| Afirmación (Claim) | CAP-06, CAP-08, CAP-13, CAP-31 |
| Hecho (Fact) | CAP-08 |
| Hallazgo (Finding) | CAP-09 |
| Hipótesis | CAP-10 |
| Conclusión | CAP-10 |
| Conocimiento | CAP-10, CAP-11, CAP-13 |
| Procedencia | CAP-06, CAP-08, CAP-09, CAP-10, CAP-13, CAP-23, CAP-30 |
| Metadatos | CAP-05, CAP-07, CAP-22, CAP-24 |
| Relación | CAP-09, CAP-31 |
| Cronología | CAP-09 |
| Contradicción | CAP-09 |
| Confianza/incertidumbre | CAP-08, CAP-10, CAP-32 |
| Lista de fuentes | CAP-05, CAP-23 |
| Notas/material | CAP-06, CAP-07 |
| Guion | CAP-13, CAP-14, CAP-17, CAP-22 |
| Storyboard | CAP-14, CAP-15, CAP-18 |
| Recursos (assets) | CAP-16, CAP-17, CAP-18, CAP-23, CAP-25 |
| Vídeo final | CAP-20, CAP-21, CAP-24, CAP-25 |
| Métricas | CAP-02, CAP-26, CAP-27, CAP-29 |
| Lecciones aprendidas | CAP-01, CAP-29 |
| Criterios | CAP-02, CAP-19 |
| Preguntas | CAP-04, CAP-10 |

**Activos de WP-0016 sin capacidad MVP asociada** (descriptivo): los **meta-activos de investigación** — Ontología/definiciones, Patrones, Matriz, Mapa de dependencias, Índice/consolidación, Glosario, Referencias bibliográficas, Dependencias(registro) — son **productos de los WP de Discovery**, no artefactos que las capacidades del MVP utilicen o produzcan según WP-0013. Por eso no aparecen vinculados a capacidades. (Constatación, no carencia a resolver.)

---

## 4. Capacidades sin activos de conocimiento asociados

> Capacidades cuyos artefactos declarados en WP-0013 **no** corresponden a ningún tipo de activo inventariado en WP-0016. No implica que carezcan de valor; solo que su producto no figura como "tipo de activo" en el inventario.

| Capacidad | Artefacto(s) declarado(s) en WP-0013 | Motivo de la ausencia |
|---|---|---|
| CAP-03 Definición de objetivos | Documento de objetivos | "Objetivos" no es un tipo inventariado en WP-0016 |
| CAP-12 Estructura | Outline / escaleta | "Escaleta/outline" no es un tipo inventariado en WP-0016 |
| CAP-28 Interacción con la comunidad | Temas recurrentes / correcciones de la audiencia | "Comentarios/feedback" no es un tipo inventariado en WP-0016 |
| CAP-33 Gestión de proyectos/casos | Contenedor del proyecto | "Contenedor/proyecto" no es un tipo inventariado en WP-0016 |

> Nota: estas ausencias se derivan estrictamente de comparar WP-0013 con WP-0016. No se propone crear activos nuevos (eso sería decisión de arquitectura, fuera de alcance).

---

## 5. Observaciones (descriptivas)

- Los activos del **bloque de evidencia** (Evidencia, Afirmación, Procedencia, Confianza/incertidumbre, Relación) concentran sus vínculos en las capacidades de **investigación** (CAP-06…CAP-10) y en las **transversales** (CAP-30/31/32), coherente con WP-0014.
- **Procedencia** es el activo con más capacidades asociadas (7), reflejando su carácter transversal ya señalado en WP-0011/0013/0014.
- Los activos de **producción** (Guion, Storyboard, Recursos, Vídeo final, Métricas, Lecciones) se vinculan a las capacidades de las fases narrativa/producción/publicación/aprendizaje.
- Las **4 capacidades sin activo inventariado** producen artefactos reales (objetivos, escaleta, feedback, contenedor) que simplemente **no** figuran como tipos en WP-0016; es una observación de cobertura, no una decisión.
- Todo lo anterior deriva de WP-0013/0014/0016; **no** se añadió ninguna relación.

---

## 6. Referencias cruzadas

- WP-0013 — MVP Capability Inventory · `docs/research/MVP-CAPABILITY-INVENTORY.md`
- WP-0014 — Capability Dependency Map · `docs/research/CAPABILITY-DEPENDENCY-MAP.md`
- WP-0016 — Knowledge Asset Inventory · `docs/research/KNOWLEDGE-ASSET-INVENTORY.md`
- (Contexto) WP-0012 — `docs/research/YOUTUBE-DOCUMENTARY-PRODUCTION-CAPABILITY-MAP.md`
- (Contexto) WP-0015 — `docs/research/DISCOVERY-INDEX.md`

---

_Fin de la matriz. Documento de síntesis: enlaza WP-0013, WP-0014 y WP-0016 sin introducir relaciones nuevas, sin inferir arquitectura, sin proponer componentes/entidades/modelos, sin DDD y sin modificar documentos existentes. Apoyo para el Principal Architect._
