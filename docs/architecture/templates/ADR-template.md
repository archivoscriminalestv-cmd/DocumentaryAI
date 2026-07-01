<!--
PLANTILLA ADR (Architecture Decision Record)
Propósito: registrar UNA decisión de arquitectura ya tomada, su contexto y sus consecuencias.
Un ADR es inmutable una vez aceptado: si la decisión cambia, se crea un ADR nuevo que
reemplaza (supersedes) al anterior, en lugar de reescribir el original.
Rellena los campos entre <...> y elimina los comentarios que no necesites.
-->

# ADR-<NNNN>: <Título de la decisión>
<!-- Título: enuncia la decisión, no el problema. P. ej. "Usar X para Y". -->

| Campo | Valor |
|---|---|
| **Identificador** | ADR-<NNNN> <!-- Identificador único y secuencial, p. ej. ADR-0001. --> |
| **Estado** | <Propuesto \| Aceptado \| Rechazado \| Obsoleto \| Reemplazado por ADR-<NNNN>> <!-- Estado de la decisión. --> |
| **Autor(es)** | <Nombre / Rol> <!-- Quién toma o documenta la decisión. --> |
| **Fecha** | <YYYY-MM-DD> <!-- Fecha en que se toma o se registra la decisión. --> |

---

## Objetivo
<!-- Qué decisión se documenta y por qué necesita registrarse. Una frase. -->
<...>

## Alcance
<!-- A qué partes del sistema/proyecto afecta esta decisión y a cuáles no. -->
- **Afecta a:** <...>
- **No afecta a:** <...>

## Contenido estructurado

### Contexto
<!-- Fuerzas en juego: requisitos, restricciones y situación que obligan a decidir. Neutral, sin la decisión todavía. -->
<...>

### Decisión
<!-- La decisión adoptada, expresada de forma clara y afirmativa. -->
<...>

### Alternativas consideradas
<!-- Opciones evaluadas y motivo de su descarte. -->
- **Opción A:** <...> — <motivo>
- **Opción B:** <...> — <motivo>

### Consecuencias
<!-- Resultados de aplicar la decisión, tanto positivos como negativos. -->
- **Positivas:** <...>
- **Negativas / compromisos:** <...>

## Referencias
<!-- RFC que originó la decisión, ADR relacionados/reemplazados, documentos externos. -->
- <...>

## Historial de cambios
<!-- Cambios de estado del ADR (no de su contenido, que es inmutable). -->

| Fecha | Autor | Cambio |
|---|---|---|
| <YYYY-MM-DD> | <Autor> | <Descripción del cambio> |
