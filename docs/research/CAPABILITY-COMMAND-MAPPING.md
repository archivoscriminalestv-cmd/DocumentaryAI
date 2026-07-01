# CAPABILITY TO COMMAND MAPPING — DocumentaryAI (WP-0022)

| Campo | Valor |
|---|---|
| **Document ID** | RES-CAPABILITY-COMMAND-MAPPING |
| **Title** | Capability to Command Mapping — DocumentaryAI |
| **Status** | Draft (synthesis) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | WP-0013, WP-0018, WP-0021 |

> **Documento de síntesis.** Traza cada capacidad del MVP (WP-0013) hacia su **acción observable** (paso previo a los futuros comandos de dominio), con activos, etapa del ciclo (WP-0018) e invariantes (WP-0021).
> **No** nombra comandos del dominio, **no** agrupa capacidades, **no** diseña APIs, **no** propone agregados y **no** modifica documentos. Deriva solo de WP-0013, WP-0018 y WP-0021.

---

## 1. Método y notas

- **Una fila por capacidad** (CAP-01…CAP-33). No se agrupan.
- **Acción observable:** expresada como **verbo/gerundio** que describe lo que hace la capacidad. **No** es un comando ni un nombre de comando; los comandos del dominio los definirá el Principal Architect (RFC-0002 / DS-0001).
- **Activos utilizados/producidos:** derivados de los artefactos "utilizados/producidos" de cada capacidad en **WP-0013**. Cuando un artefacto de WP-0013 **no** es un activo de conocimiento inventariado, se marca `(art. no inventariado: …)`.
- **Etapa:** del ciclo de vida de **WP-0018** (E1 Investigación · E2 Narrativa · E3 Producción/Post · E4 Publicación · E5 Post-publicación/Aprendizaje · TR Transversal).
- **Invariantes:** las de **WP-0021** que referencian explícitamente esa capacidad.

> **Invariantes transversales (aplican a todas/casi todas, no se repiten por fila):** INV-002 y INV-017 (Research Centric), INV-009 e INV-019 (AI Independence), INV-010 (Capability Independence), INV-026 (prerrequisitos funcionales, en capacidades con dependencias).

---

## 2. Matriz de trazabilidad

| CAP | Acción observable (verbo, no comando) | Activos utilizados | Activos producidos | Etapa | Invariantes (WP-0021) | Observaciones |
|---|---|---|---|---|---|---|
| CAP-01 | Idear / generar ideas | Lecciones aprendidas | (art. no inventariado: banco de ideas) | E1 | INV-011 | Entrada del ciclo; realimentada por CAP-29 |
| CAP-02 | Seleccionar tema | Métricas, Criterios | (art. no inventariado: ficha de tema) | E1 | — (transversales) | Decisión editorial |
| CAP-03 | Definir objetivos | — | (art. no inventariado: objetivos) | E1 | — (transversales) | Sin activo inventariado |
| CAP-04 | Planificar investigación | — | Preguntas | E1 | — (transversales) | — |
| CAP-05 | Descubrir/localizar fuentes | — | Lista de fuentes, Metadatos | E1 | INV-011 | — |
| CAP-06 | Recolectar información | Lista de fuentes | Notas/material, Observación, Afirmación, Evidencia, Procedencia | E1 | INV-003, INV-004, INV-007, INV-008, INV-011, INV-020 | Origen de evidencia/procedencia |
| CAP-07 | Organizar materiales | Notas/material | Notas/material (organizado), Metadatos | E1 | INV-008, INV-011 | — |
| CAP-08 | Verificar | Afirmación, Evidencia, Procedencia, Confianza | Hecho, Confianza | E1 | INV-003, INV-005, INV-007, INV-020, INV-021, INV-022 | Núcleo de credibilidad |
| CAP-09 | Analizar | Evidencia, Procedencia | Hallazgo, Cronología, Contradicción, Relación | E1 | INV-007, INV-020, INV-022 | — |
| CAP-10 | Consolidar conocimiento | Hallazgo | Hipótesis, Conclusión, Conocimiento, Confianza, Preguntas | E1 | INV-001, INV-003, INV-006, INV-007, INV-016, INV-020, INV-023 | Salida bisagra hacia narrativa |
| CAP-11 | Diseñar narrativa | Conocimiento | (art. no inventariado: concepto narrativo) | E2 | INV-001, INV-007 | Contenido derivado del conocimiento |
| CAP-12 | Estructurar | (art. no inventariado: concepto) | (art. no inventariado: escaleta) | E2 | INV-007 | Sin activo inventariado |
| CAP-13 | Redactar guion | Conocimiento, Afirmación, Procedencia | Guion | E2 | INV-001, INV-004, INV-005, INV-007, INV-011 | Referencias afirmación↔fuente |
| CAP-14 | Esbozar storyboard | Guion | Storyboard | E2 | INV-007 | — |
| CAP-15 | Planificar visualmente | Storyboard | (art. no inventariado: guía de estilo) | E2 | — (transversales) | — |
| CAP-16 | Producir recursos | (art. no inventariado: plan visual) | Recursos (assets) | E3 | INV-011 | Sujeto a CAP-23 (derechos) |
| CAP-17 | Narrar / locutar | Guion | Recursos (assets, sonoros) | E3 | INV-011 | — |
| CAP-18 | Editar / montar | Recursos, Storyboard | (art. no inventariado: máster) | E3 | INV-001 | Converge CAP-16/CAP-17 |
| CAP-19 | Revisar (calidad) | (art. no inventariado: máster), verificación | Criterios (checklist QA) | E3 | INV-026 | Bucle local con CAP-18 |
| CAP-20 | Exportar / renderizar | (art. no inventariado: máster) | Vídeo final | E3 | — (transversales) | — |
| CAP-21 | Empaquetar | Vídeo final | (art. no inventariado: título/miniatura) | E4 | INV-011 | — |
| CAP-22 | Optimizar metadatos | Guion | Metadatos | E4 | INV-011 | — |
| CAP-23 | Comprobar derechos | Recursos, Lista de fuentes | Procedencia (licencias/atribuciones) | E4 | INV-004, INV-024, INV-026 | Transversal a CAP-05/CAP-16 |
| CAP-24 | Publicar | Vídeo final, Metadatos | (art. no inventariado: registro de publicación) | E4 | INV-026 | Converge CAP-20/21/22/23 |
| CAP-25 | Distribuir | Vídeo final, Recursos | (art. no inventariado: clips) | E4 | INV-011 | "Fuera del MVP" (WP-0013) |
| CAP-26 | Medir | (art. no inventariado: registro de publicación) | Métricas | E5 | INV-011, INV-013, INV-020 | Núcleo del aprendizaje |
| CAP-27 | Interpretar retroalimentación | Métricas | (art. no inventariado: informe de desempeño) | E5 | INV-013 | — |
| CAP-28 | Interactuar con la comunidad | (art. no inventariado: comentarios) | (art. no inventariado: temas/correcciones) | E5 | — (transversales) | "Fuera del MVP" (WP-0013); sin activo inventariado |
| CAP-29 | Aprender / capitalizar | (art. no inventariado: informe), Métricas | Lecciones aprendidas | E5 | INV-001, INV-012, INV-013, INV-016, INV-018 | Cierra el bucle hacia CAP-01 |
| CAP-30 | Registrar procedencia | Materiales, Afirmación | Procedencia | TR | INV-004, INV-015, INV-020, INV-024 | Transversal (E1–E2) |
| CAP-31 | Gestionar afirmaciones/evidencia | Observación, Notas/material | Afirmación, Evidencia, Relación | TR | INV-003, INV-005, INV-021 | Sustrato de evidencia |
| CAP-32 | Calificar incertidumbre | Afirmación, Source | Confianza/incertidumbre | TR | INV-025 | — |
| CAP-33 | Contener/gestionar proyecto | (art. no inventariado: ficha de tema, objetivos) | (art. no inventariado: contenedor) | TR | INV-002, INV-017 | Contiene CAP-04…CAP-29 |

---

## 3. Observaciones de trazabilidad

- **Acciones, no comandos:** todas las "acciones observables" son verbos descriptivos; **ningún** nombre corresponde a un comando del dominio (pendiente de RFC-0002 / DS-0001).
- **Activos no inventariados:** varias capacidades producen artefactos (objetivos, escaleta, máster, packaging, registros, comentarios, contenedor) que **no** figuran como activos de conocimiento inventariados (coherente con WP-0017 §4 y WP-0019). Se marcan, no se crean.
- **Concentración de invariantes:** las capacidades de evidencia/conocimiento (CAP-06, CAP-08, CAP-10, CAP-13, CAP-30, CAP-31) acumulan la mayoría de invariantes de **trazabilidad** (INV-004/005/007/020/024) y **epistemológicas** (INV-003/021/022/023); CAP-29 concentra las de **aprendizaje** (INV-012/013/016/018).
- **Capacidades sin invariante específica:** CAP-02, CAP-03, CAP-04, CAP-15, CAP-28 solo quedan bajo las **invariantes transversales**; se anota, no se decide.
- **Etapas:** E1 (Investigación) concentra el mayor número de capacidades y de invariantes; TR (transversales) sostiene el sustrato de evidencia/procedencia y el contenedor.
- Todo deriva de WP-0013, WP-0018 y WP-0021; **no** se ha inventado ni nombrado ningún comando.

---

## 4. Referencias cruzadas

- WP-0013 — MVP Capability Inventory · `docs/research/MVP-CAPABILITY-INVENTORY.md`
- WP-0018 — Research Lifecycle Extraction · `docs/research/RESEARCH-LIFECYCLE-EXTRACTION.md`
- WP-0021 — Domain Invariant Extraction · `docs/research/DOMAIN-INVARIANT-EXTRACTION.md`

---

_Fin del mapeo. Documento de síntesis: una fila por capacidad, acción como verbo observable (no comando), derivado solo de WP-0013/0018/0021. No nombra comandos, no agrupa capacidades, no diseña APIs, no propone agregados y no modifica documentos existentes._
