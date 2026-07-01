# Contributing — DocumentaryAI

Este documento define las reglas del flujo de trabajo del repositorio. No introduce decisiones de dominio ni de arquitectura.

## Roles y flujo

- **El Principal Architect decide.** La arquitectura, la metodología y la documentación normativa las define el Principal Architect.
- **Claude (Developer) implementa.** Claude ejecuta las especificaciones aprobadas: analiza, propone un plan, espera aprobación, implementa, verifica y entrega un informe. No rediseña la arquitectura por iniciativa propia.
- **El repositorio es la única fuente de verdad.** Si un documento aprobado existe en el repositorio, prevalece sobre cualquier conversación. Un documento aprobado no se regenera desde cero; se evoluciona o se reemplaza de forma deliberada.
- **Ningún documento derivado puede adelantarse a su fuente normativa.** Un documento que dependa de otro (p. ej. una SPEC que dependa de un RFC, o un catálogo que dependa de un modelo) no puede crearse ni completarse antes de que exista y esté aprobada su fuente normativa.

## Reglas de documentación

- Toda la documentación oficial vive bajo `docs/` (ver `docs/README.md`).
- Las plantillas oficiales viven bajo `templates/`.
- El front matter de los documentos sigue `docs/architecture/Document-Header-Standard.md` (tabla Markdown, sin YAML).
- Tipos y numeración:
  - **ARCH-NNNN** — documentos de arquitectura (`docs/architecture/`).
  - **ADR-NNNN** — decisiones de arquitectura (`docs/adr/`).
  - **RFC-NNNN** — propuestas (`docs/rfc/`).
  - **SPEC-NNNN** — especificaciones (`docs/spec/`).
- Los identificadores son secuenciales, de cuatro dígitos, únicos e irrepetibles; los asigna el Principal Architect.

## Reglas de cambio

- Cada cambio es pequeño y coherente; un commit representa una única mejora.
- No se modifican documentos aprobados de otro autor sin instrucción explícita.
- Antes de implementar un cambio estructural se requiere una especificación previa aprobada.
- Cada tarea se cierra con un informe: qué cambió, archivos, motivo, riesgos y próximos pasos.

## Referencias

- `docs/README.md` — organización documental.
- `docs/governance/PROJECT-CHARTER.md` — gobernanza del proyecto.
- `docs/architecture/Document-Header-Standard.md` — estándar de cabecera.
