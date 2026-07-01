# ADR-0002 — Knowledge Accumulation is the Core Value

Status: Approved

Author: Principal Architect

---

# 1. Context

DocumentaryAI no existe para producir documentos, vídeos o investigaciones aisladas.

El propósito del sistema es incrementar de forma continua el patrimonio de conocimiento reutilizable.

Cada Research representa un esfuerzo temporal.

El conocimiento obtenido debe sobrevivir a esa Research.

Era necesario decidir cuál constituye el activo permanente del dominio.

---

# 2. Decision

La Knowledge Base constituye el activo permanente de DocumentaryAI.

Toda Research existe para incrementar la Knowledge Base.

El éxito del sistema no se mide por el número de investigaciones realizadas.

Se mide por el incremento acumulado del conocimiento reutilizable.

---

# 3. Rationale

## 3.1 Research es temporal

Toda Research posee un inicio y un final.

Puede archivarse.

Puede completarse.

Puede abandonarse.

---

## 3.2 El conocimiento permanece

El conocimiento validado continúa siendo útil después de finalizar una Research.

Debe permanecer disponible para futuras investigaciones.

---

## 3.3 El aprendizaje es acumulativo

Cada nueva Research debe partir del conocimiento previamente adquirido.

El sistema mejora porque aprende.

No porque automatiza.

---

# 4. Consequences

La eliminación de una Research nunca implica la pérdida del conocimiento validado.

La reutilización de conocimiento será un objetivo explícito del dominio.

Las futuras capacidades deberán favorecer el enriquecimiento continuo de la Knowledge Base.

---

# 5. Relationship with ADR-0001

ADR-0001 define la unidad operacional.

ADR-0002 define el activo permanente.

Ambas decisiones son complementarias.

No existe conflicto entre ellas.

Research ejecuta.

Knowledge Base preserva.

---

# 6. Alternatives Considered

## Research como activo principal

Descartada.

Research representa trabajo.

No representa el valor acumulado del sistema.

---

## Document Repository

Descartado.

El dominio no gestiona documentos.

Gestiona conocimiento.

---

# 7. Implications

Esta decisión no define:

* entidades;
* agregados;
* persistencia;
* APIs;
* arquitectura técnica.

Únicamente establece el activo permanente del dominio.

---

# 8. Related Documents

* ARCH-0002 — Domain Philosophy
* ADR-0001 — Research is the Operational Unit
* RFC-0002 — Domain Model
* WP-0020
* WP-0021
