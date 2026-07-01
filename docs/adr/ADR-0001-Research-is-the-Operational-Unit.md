# ADR-0001 — Research is the Operational Unit

Status: Accepted

Author: Principal Architect

---

# 1. Context

DocumentaryAI tiene como objetivo incrementar de forma continua el conocimiento reutilizable del sistema mediante la producción de contenido basado en investigación.

Durante la fase Discovery aparecieron dos posibles centros del dominio:

* Research
* Knowledge Base

La evidencia recopilada demuestra que ambos son fundamentales, pero cumplen responsabilidades distintas.

Era necesario decidir cuál constituye la unidad operacional del sistema.

---

# 2. Decision

La unidad operacional de DocumentaryAI es **Research**.

Toda actividad ejecutable por el sistema ocurre dentro de una Research.

Una Research representa una investigación delimitada en el tiempo y en el objetivo.

No representa el conocimiento permanente del sistema.

Su función es transformar información externa en conocimiento reutilizable.

---

# 3. Rationale

## 3.1 Toda capacidad pertenece a una investigación

Las capacidades identificadas durante Discovery forman parte del ciclo de una Research.

No existen capacidades aisladas.

## 3.2 Una Research posee límites naturales

Una investigación:

* comienza;
* incorpora fuentes;
* genera evidencia;
* produce conocimiento;
* puede finalizar.

Estos límites permiten gestionar el trabajo del sistema sin imponer restricciones sobre el conocimiento acumulado.

## 3.3 El conocimiento trasciende las investigaciones

El conocimiento no pertenece únicamente a una Research.

Debe poder reutilizarse posteriormente.

Por tanto, no puede utilizarse como unidad operacional.

---

# 4. Consequences

Toda ejecución del sistema deberá iniciarse mediante una Research.

Las capacidades del MVP operarán siempre dentro del contexto de una Research.

Los procesos futuros también deberán poder asociarse a una Research.

La finalización de una Research nunca implica la pérdida del conocimiento generado.

---

# 5. Alternatives Considered

## Knowledge Base como unidad operacional

Descartada.

La Knowledge Base representa el patrimonio de conocimiento del sistema.

No constituye una unidad de trabajo.

No posee un inicio ni un final claramente definidos.

## Workspace como unidad operacional

Descartada.

Workspace representa un espacio organizativo.

No describe un proceso.

---

# 6. Implications

Esta decisión no define:

* entidades;
* agregados;
* persistencia;
* comandos;
* APIs;
* arquitectura técnica.

Únicamente establece el límite operativo del dominio.

---

# 7. Related Documents

* ARCH-0002 — Domain Philosophy
* RFC-0002 — Core Domain Rules (Pending)
* SPEC-0001 — Research Lifecycle (Skeleton)
* WP-0013
* WP-0018
* WP-0020
