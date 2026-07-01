<!--
PLANTILLA Review (Informe de Revisión)
Propósito: registrar el resultado de una revisión (de código, documento, diseño o entregable):
hallazgos clasificados por severidad y recomendaciones.
Un Review observa y recomienda; no toma decisiones de arquitectura (eso es un ADR).
Rellena los campos entre <...> y elimina los comentarios que no necesites.
-->

# REVIEW-<NNNN>: <Título de la revisión>
<!-- Título: qué se ha revisado. -->

| Campo | Valor |
|---|---|
| **Identificador** | REVIEW-<NNNN> <!-- Identificador único, p. ej. REVIEW-0001. --> |
| **Estado** | <Borrador \| Completada \| Cerrada> <!-- Estado del informe de revisión. --> |
| **Autor(es)** | <Nombre / Rol del revisor> <!-- Quién realiza la revisión. --> |
| **Fecha** | <YYYY-MM-DD> <!-- Fecha de la revisión. --> |

---

## Objetivo
<!-- Qué se revisa y con qué finalidad. -->
<...>

## Alcance
<!-- Qué elementos se han revisado y cuáles han quedado fuera de la revisión. -->
- **Revisado:** <...>
- **No revisado:** <...>

## Contenido estructurado

### Resumen de la revisión
<!-- Valoración general y conclusión principal. -->
<...>

### Hallazgos
<!-- Hallazgos clasificados por severidad. Cada uno identificable y trazable. -->

#### Críticos
<!-- Problemas que deben resolverse de inmediato. -->
- <...>

#### Importantes
<!-- Problemas relevantes que conviene resolver pronto. -->
- <...>

#### Menores
<!-- Problemas de bajo impacto o mejoras opcionales. -->
- <...>

### Recomendaciones
<!-- Para cada recomendación: Problema, Impacto y Recomendación. No implica implementarlas. -->

#### R-1
- **Problema:** <...>
- **Impacto:** <...>
- **Recomendación:** <...>

## Referencias
<!-- Documentos, RFC/ADR/SPEC o material revisado y enlaces de apoyo. -->
- <...>

## Historial de cambios

| Fecha | Autor | Cambio |
|---|---|---|
| <YYYY-MM-DD> | <Autor> | <Descripción del cambio> |
