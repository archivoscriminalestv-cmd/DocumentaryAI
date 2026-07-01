# PROJECT CHARTER — DocumentaryAI

| Campo | Valor |
|---|---|
| **Document ID** | GOV-PROJECT-CHARTER |
| **Title** | Project Charter — DocumentaryAI |
| **Status** | Approved |
| **Version** | 1.0 |
| **Author** | Claude Code (Developer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect, Project Director |
| **Related Documents** | `docs/DEVELOPMENT_GUIDE.md`, `docs/TEAM_CHARTER.md`, `docs/architecture/` |

> Documento de **gobernanza del proyecto**. Es la referencia oficial para la organización del equipo, los roles y la metodología de trabajo.
> **No** forma parte de la arquitectura del sistema ni la define; forma parte de la **gobernanza**.
> Recoge y consolida decisiones ya aprobadas por el Principal Architect; no introduce decisiones nuevas.

---

## 1. Purpose

Este Project Charter establece **cómo se organiza y se trabaja** en DocumentaryAI: el propósito del proyecto, sus principios de gobernanza, los roles, la jerarquía de decisiones y de documentación, y la metodología de colaboración (incluida la colaboración con IA).

Su objetivo es garantizar continuidad, coherencia y trazabilidad a lo largo del tiempo, de modo que cualquier persona o asistente de IA que se incorpore pueda entender **quién decide qué**, **cómo se trabaja** y **dónde reside la verdad** del proyecto.

---

## 2. Project Vision

DocumentaryAI es una **plataforma profesional** —no un experimento— para **investigar casos criminales reales mediante inteligencia artificial**.

La plataforma evolucionará para poder: gestionar proyectos de investigación, importar documentación, construir cronologías, detectar contradicciones, generar hipótesis, redactar guiones documentales y producir vídeos de forma asistida por agentes de IA.

La prioridad absoluta es construir una arquitectura **limpia, escalable y mantenible** durante muchos años. Esta sección describe la visión como **contexto de gobernanza**; el diseño técnico que la realiza se define en la documentación de arquitectura, no aquí.

---

## 3. Governance Principles

1. **El repositorio tiene prioridad sobre la conversación.** Si existe un documento aprobado en el repositorio, es la fuente de verdad; no se regenera desde cero salvo decisión deliberada de reemplazo.
2. **La arquitectura la define el Principal Architect.** Nadie modifica la arquitectura por iniciativa propia.
3. **Evolución progresiva.** La estructura y la complejidad crecen solo cuando existe una necesidad real; se evita la arquitectura especulativa.
4. **Claridad por encima de sofisticación.** Ante la duda entre una solución más sofisticada y otra más clara, se elige la más clara.
5. **Trazabilidad de decisiones.** Las decisiones relevantes quedan registradas en documentos versionados (p. ej. ADR), no solo en conversaciones.
6. **Separación de responsabilidades.** Cada rol, documento y módulo tiene un propósito único y delimitado.

---

## 4. Project Roles

| Rol | Quién | Responsabilidad principal |
|---|---|---|
| **Project Director** | Usuario (Albert) | Dirección del proyecto; objetivos y prioridades; aprobación final de alto nivel. |
| **Principal Architect** | ChatGPT | Define la arquitectura y la metodología; redacta la documentación oficial de arquitectura (RFC, ADR, ARCH, SPEC); aprueba planes antes de su implementación. |
| **Developer** | Claude Code (asistente de IA) | Implementa las especificaciones aprobadas; refactoriza, prueba, corrige y documenta el código; analiza, propone planes y entrega informes. No rediseña la arquitectura por iniciativa propia. |

El Developer puede **proponer** mejoras, pero **espera aprobación** antes de implementarlas.

---

## 5. Decision Hierarchy

1. **Decisiones de dirección y prioridades** → Project Director.
2. **Decisiones de arquitectura y metodología** → Principal Architect.
3. **Decisiones de implementación** (dentro de una especificación aprobada) → Developer.

Reglas:
- El Developer **no toma decisiones arquitectónicas**; si detecta una mejora, la **describe, expone ventajas/inconvenientes y espera aprobación**.
- Toda modificación estructural del proyecto requiere una **especificación previa aprobada**.
- En caso de conflicto entre conversación y repositorio, **prevalece el repositorio**.

---

## 6. Documentation Hierarchy

La documentación se organiza en dos cuerpos:

- **Gobernanza** (`docs/governance/`): este Charter y documentos de organización del proyecto.
- **Arquitectura** (`docs/architecture/`): documentación técnica oficial.

Tipos de documento de arquitectura y su rol (definidos en los estándares y plantillas del repositorio):

| Tipo | Rol |
|---|---|
| **RFC** | Propuesta abierta a discusión (el "qué" y el "porqué"). |
| **ADR** | Registro de una decisión de arquitectura ya tomada. |
| **ARCH** | Descripción de la arquitectura (componentes, relaciones, vistas). |
| **SPEC** | Especificación de qué debe construirse y sus criterios de aceptación. |
| **Review** | Informe de revisión (hallazgos y recomendaciones). |
| **Standard / Index** | Estándares (p. ej. cabecera documental) e índices de navegación. |

Principios documentales:
- Todos los documentos oficiales siguen el **estándar de cabecera** acordado.
- El catálogo de estados, el esquema de identificadores y la política de relaciones entre tipos los define el Principal Architect.
- El repositorio prevalece como fuente de verdad.

---

## 7. Working Process

El trabajo se organiza por **Work Packages (WP)** y por **fases**.

Flujo de un Work Package:
1. El Principal Architect (o el Director) emite una **especificación**.
2. El Developer **analiza** el impacto y verifica que respeta la arquitectura existente.
3. El Developer **propone un plan** y **espera aprobación**.
4. Tras la aprobación, el Developer **implementa únicamente lo autorizado**, minimizando cambios.
5. El Developer **verifica** que el proyecto sigue funcionando y no rompe nada existente.
6. El Developer entrega un **informe**: qué cambió, archivos modificados, justificación, riesgos y próximos pasos.

Hoja de ruta oficial por fases (gobernanza del avance):
1. Saneamiento del proyecto. **(cerrada)**
2. Arquitectura base.
3. Sistema de proyectos.
4. Gestión documental.
5. Cronologías (núcleo central de DocumentaryAI).
6. Investigación (hipótesis, contradicciones, relaciones).
7. Integración de IA (la IA es una herramienta del sistema, no el sistema).
8. Generación de guiones documentales.
9. Producción audiovisual.

---

## 8. Engineering Principles

Principios de ingeniería aprobados (detallados en `docs/DEVELOPMENT_GUIDE.md`):

- **Prioridades:** claridad, simplicidad, mantenibilidad, escalabilidad.
- **Una responsabilidad por módulo**; evitar archivos enormes.
- **Código legible**: la legibilidad prima sobre la concisión.
- **Calidad**: nombres descriptivos, sin duplicación, sin código muerto, funciones cortas; tipado y estilo según las normas del proyecto.
- **Separación capa de presentación ↔ lógica de negocio**: la interfaz no contiene lógica de negocio; la lógica de negocio no depende de la interfaz.
- **Refactor solo** cuando simplifica, elimina duplicación o mejora la claridad **sin cambiar el comportamiento**.
- **Dependencias**: justificarlas; preferir la biblioteca estándar cuando sea suficiente.
- **Git**: cambios pequeños y coherentes; cada commit representa una única mejora.

---

## 9. Collaboration with AI

- La IA (Claude Code) actúa como **Developer bajo gobernanza**: implementa lo aprobado, no rediseña por iniciativa propia.
- Antes de cualquier cambio estructural, la IA **propone un plan y espera aprobación**.
- La IA entrega **informes** al cerrar cada tarea (cambios, archivos, riesgos, próximos pasos).
- En el producto, **los proveedores de IA deberán poder intercambiarse**; no se acopla el proyecto a un único proveedor. La IA es **una herramienta del sistema, no el sistema en sí**, y se incorpora cuando el núcleo ya existe.
- El **repositorio prevalece sobre la conversación** también para la IA: ante una memoria/contexto de chat que contradiga un documento aprobado, manda el documento.

---

## 10. Change Management

- Toda modificación estructural requiere **especificación previa aprobada**.
- Los cambios se realizan en **incrementos pequeños y coherentes**, con commits de una sola mejora.
- Un documento aprobado **no se regenera desde cero**; se **evoluciona** o se **reemplaza deliberadamente** (registrando el reemplazo).
- Las decisiones de arquitectura se documentan (ADR) para su trazabilidad.
- El alcance de cada tarea se respeta estrictamente: no se añaden cambios no solicitados.

---

## 11. Success Criteria

El proyecto se considera bien gobernado cuando:

- La plataforma es **sólida, mantenible y escalable**, y avanza según la hoja de ruta por fases.
- Los **refactors no alteran el comportamiento** existente salvo autorización explícita.
- La **documentación es coherente** con el estado real del repositorio y navegable.
- Cada cambio es **trazable** (especificación → plan aprobado → implementación → informe).
- Los **roles y la jerarquía de decisiones** se respetan en todas las tareas.
- El **repositorio se mantiene como fuente de verdad** única.

---

## 12. Document Maintenance

- **Owner:** Principal Architect (responsable del contenido y de su evolución).
- Este documento sigue el **estándar de cabecera** del proyecto y se actualiza incrementando su `Version` y su `Last Updated`.
- Las modificaciones se registran en el **Change History**.
- No se reescribe desde cero: se evoluciona o se reemplaza de forma deliberada.
- La consolidación con `docs/TEAM_CHARTER.md` y `docs/DEVELOPMENT_GUIDE.md` (que contienen las decisiones de origen) la decide el Principal Architect.

---

## 13. Change History

| Fecha | Versión | Autor | Cambio |
|---|---|---|---|
| 2026-06-28 | 1.0 | Claude Code (Developer) | Creación inicial del Project Charter a partir de las decisiones ya aprobadas. |

---

_Documento de gobernanza. No define la arquitectura del sistema, no modifica RFC/ADR, no crea SPEC y no contiene código._
