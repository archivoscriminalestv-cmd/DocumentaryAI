# RESEARCH LIFECYCLE EXTRACTION — DocumentaryAI (WP-0018)

| Campo | Valor |
|---|---|
| **Document ID** | RES-RESEARCH-LIFECYCLE |
| **Title** | Research Lifecycle Extraction — DocumentaryAI |
| **Status** | Draft (extraction) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | WP-0012, WP-0013, WP-0014, WP-0017 (ver §7) |

> **Documento de extracción.** Deriva el ciclo de vida **implícito** de una investigación dentro del MVP, **exclusivamente** a partir de WP-0012, WP-0013, WP-0014 y WP-0017.
> **No** propone estados del dominio, **no** define entidades, **no** crea un modelo de ciclo de vida, **no** infiere arquitectura y **no** modifica documentos existentes.
> Las etapas son **fases de proceso ya documentadas** (mapa de WP-0012 / grupos de WP-0013); los bucles/bifurcaciones señalados son **solo** los que WP-0014 documenta.

---

## 1. Objetivo y método

Hacer explícito el flujo de principio a fin que una investigación recorre en el MVP, leyéndolo de la evidencia existente.

**Método (sin añadir nada):**
- **Etapas:** las fases ya documentadas en el mapa de capacidades de WP-0012 y en las agrupaciones de WP-0013 (G1…G5), más las transversales (G6).
- **Capacidades por etapa:** las que WP-0013/WP-0014 asignan a cada grupo.
- **Activos utilizados/producidos:** los de WP-0017 (que a su vez derivan de los artefactos de WP-0013).
- **Entradas/salidas:** los artefactos de frontera entre etapas según WP-0013.
- **Bifurcaciones/bucles:** únicamente los declarados en WP-0014 (§4 dependencias y §8 ciclos).

> Aclaración: "etapa" = **fase del proceso** documentada; **no** es un estado del dominio ni un estado de una entidad. No se introduce ningún modelo nuevo.

---

## 2. Etapas identificadas

### Etapa 1 — Investigación *(grupo G1; WP-0012 fase "Pre-producción/Investigación")*
- **Capacidades:** CAP-01 Ideación, CAP-02 Selección de tema, CAP-03 Objetivos, CAP-04 Planificación, CAP-05 Descubrimiento de fuentes, CAP-06 Recolección, CAP-07 Organización, CAP-08 Verificación, CAP-09 Análisis, CAP-10 Construcción de conocimiento. *(transversales activas: CAP-30, CAP-31, CAP-32; contenedor: CAP-33)*
- **Activos utilizados:** Lecciones aprendidas, Métricas, Criterios, Preguntas, Lista de fuentes, Notas/material, Observación, Afirmación, Evidencia, Procedencia, Confianza/incertidumbre.
- **Activos producidos:** Lista de fuentes, Notas/material, Observación, Afirmación, Evidencia, Metadatos, Hecho, Hallazgo, Cronología, Contradicción, Relación, Hipótesis, Conclusión, Conocimiento, Procedencia, Confianza/incertidumbre, Preguntas.
- **Entrada de la etapa:** tema/idea (realimentada por Lecciones aprendidas de la Etapa 5).
- **Salida de la etapa:** **base de conocimiento del proyecto** (hipótesis, conclusiones, evidencia con procedencia y confianza).

### Etapa 2 — Diseño narrativo *(grupo G2; WP-0012 fase "Diseño narrativo")*
- **Capacidades:** CAP-11 Diseño narrativo, CAP-12 Estructura, CAP-13 Guion, CAP-14 Storyboard, CAP-15 Planificación visual.
- **Activos utilizados:** Conocimiento, Afirmación, Procedencia, Guion, Storyboard.
- **Activos producidos:** Guion (con referencias afirmación↔fuente), Storyboard. *(además: ángulo/estructura/guía de estilo/lista de recursos — no inventariados como activos en WP-0016, cf. WP-0017 §4)*
- **Entrada de la etapa:** base de conocimiento + objetivos.
- **Salida de la etapa:** **guion + storyboard** (y plan visual).

### Etapa 3 — Producción / Post-producción *(grupo G3; WP-0012 fase "Producción/Post")*
- **Capacidades:** CAP-16 Producción de recursos, CAP-17 Locución, CAP-18 Edición, CAP-19 Control de calidad, CAP-20 Exportación.
- **Activos utilizados:** Guion, Storyboard, Recursos (assets), Criterios.
- **Activos producidos:** Recursos (assets), Vídeo final.
- **Entrada de la etapa:** guion + storyboard (+ plan visual).
- **Salida de la etapa:** **vídeo final** (archivo exportado, con subtítulos/derivados).

### Etapa 4 — Publicación *(grupo G4; WP-0012 fase "Publicación")*
- **Capacidades:** CAP-21 Empaquetado, CAP-22 Metadatos/SEO, CAP-23 Derechos, CAP-24 Publicación, CAP-25 Distribución.
- **Activos utilizados:** Vídeo final, Metadatos, Recursos (assets), Lista de fuentes, Procedencia.
- **Activos producidos:** Metadatos, Vídeo final (publicado). *(además: registro de publicación/URL, packaging, registro de licencias — no inventariados, cf. WP-0017 §4)*
- **Entrada de la etapa:** vídeo final + packaging + metadatos + estado de cumplimiento.
- **Salida de la etapa:** **vídeo publicado** (y acciones de distribución).

### Etapa 5 — Post-publicación / Aprendizaje *(grupo G5; WP-0012 fase "Post-publicación/Aprendizaje")*
- **Capacidades:** CAP-26 Métricas, CAP-27 Retroalimentación, CAP-28 Comunidad, CAP-29 Aprendizaje.
- **Activos utilizados:** Métricas. *(además: comentarios/feedback — no inventariados, cf. WP-0017 §4)*
- **Activos producidos:** Métricas, Lecciones aprendidas. *(además: informe de desempeño — no inventariado)*
- **Entrada de la etapa:** vídeo publicado.
- **Salida de la etapa:** **métricas + lecciones aprendidas** → realimentan la Etapa 1 (CAP-29 → CAP-01, según WP-0014).

### Transversal — Sustrato y contenedor *(grupo G6)*
- **Capacidades:** CAP-30 Procedencia, CAP-31 Afirmaciones/evidencia, CAP-32 Incertidumbre/confianza, CAP-33 Proyecto/caso.
- **Papel (según WP-0014):** CAP-30/31/32 aportan sustrato a las Etapas 1–2 (CAP-06→CAP-08/09/10/13); CAP-33 contiene CAP-04…CAP-29 a lo largo de todo el ciclo.

---

## 3. Flujo completo (principio a fin)

> Representación textual del flujo derivado de WP-0014. Las flechas son dependencias funcionales documentadas; no son arquitectura.

```
[ CAP-33 Proyecto/caso : contiene todo el ciclo ]

ETAPA 1 — INVESTIGACIÓN
  CAP-01 → CAP-02 → CAP-03 → CAP-04 → CAP-05 → CAP-06 → CAP-07 → CAP-08 → CAP-09 → CAP-10
     (transversales: CAP-30, CAP-31 desde CAP-06 ; CAP-32 desde CAP-31 ; usadas por CAP-08/09/10)
        │ salida: base de conocimiento
        ▼
ETAPA 2 — DISEÑO NARRATIVO
  CAP-11 → CAP-12 → CAP-13 → CAP-14 → CAP-15
        │ salida: guion + storyboard
        ▼
ETAPA 3 — PRODUCCIÓN / POST
  CAP-16 ┐
  CAP-17 ┴► CAP-18 ⇄ CAP-19 → CAP-20        (bucle local de revisión CAP-18↔CAP-19)
        │ salida: vídeo final
        ▼
ETAPA 4 — PUBLICACIÓN
  CAP-20 → { CAP-21, CAP-22, CAP-23 } → CAP-24 → CAP-25     (CAP-23 transversal a CAP-05/CAP-16)
        │ salida: vídeo publicado
        ▼
ETAPA 5 — POST-PUBLICACIÓN / APRENDIZAJE
  CAP-24 → { CAP-26, CAP-28 } → CAP-27 → CAP-29
        │
        └──────── (bucle macro de aprendizaje) ───────► CAP-01 (ETAPA 1)
```

---

## 4. Bifurcaciones y bucles documentados (solo de WP-0014)

> Únicamente los que WP-0014 declara (§4 dependencias, §8 ciclos). No se añaden otros.

**Bucles (ciclos funcionales):**
1. **Bucle macro de aprendizaje:** `CAP-24 → CAP-26 → CAP-27 → CAP-29 → CAP-01 → …` (con CAP-28 alimentando CAP-27 y CAP-29). Conecta la Etapa 5 con la Etapa 1.
2. **Bucle local de revisión:** `CAP-18 → CAP-19 → (correcciones) → CAP-18`, dentro de la Etapa 3.

**Bifurcaciones / convergencias:**
- **Convergencia** (Etapa 3): `CAP-16` y `CAP-17` confluyen en `CAP-18`.
- **Bifurcación** (Etapa 3→4): `CAP-20` habilita `CAP-21`, `CAP-22` y `CAP-24`.
- **Convergencia** (Etapa 4): `CAP-21`, `CAP-22`, `CAP-23` confluyen en `CAP-24`.
- **Bifurcación** (Etapa 4→5): `CAP-24` habilita `CAP-25`, `CAP-26` y `CAP-28`.

**Transversalidad** (no es bucle): CAP-23 actúa sobre CAP-05 y CAP-16; CAP-30/31/32 aportan sustrato a varias capacidades de las Etapas 1–2.

> Fuera de lo anterior, el flujo es una **cadena dirigida** (acíclica) según WP-0014.

---

## 5. Capacidades transversales en el ciclo

| Capacidad | Actúa en | Naturaleza (según WP-0014) |
|---|---|---|
| CAP-30 Procedencia | Etapas 1–2 (y registro continuo) | Acompaña material y afirmaciones (CAP-06→CAP-08/09/10/13) |
| CAP-31 Afirmaciones/evidencia | Etapas 1–2 | Sustrato de evidencia (CAP-06→CAP-08/09/10/13) |
| CAP-32 Incertidumbre/confianza | Etapa 1 | Califica afirmaciones/conclusiones (CAP-08, CAP-10) |
| CAP-23 Derechos | Etapas 1, 3, 4 | Comprobación en fuentes, recursos y publicación |
| CAP-33 Proyecto/caso | Todo el ciclo | Contenedor (contiene CAP-04…CAP-29) |

---

## 6. Observaciones (descriptivas)

- El ciclo extraído es una **secuencia de 5 etapas** con **dos bucles** (macro de aprendizaje y local de revisión) y varias **convergencias/bifurcaciones**, todo ya presente en WP-0014.
- La **base de conocimiento** (salida de la Etapa 1) es el activo que conecta la investigación con la narrativa; el **vídeo final** y las **métricas/lecciones** son los activos de frontera de las etapas posteriores.
- Las **capacidades transversales** (procedencia, evidencia, incertidumbre, derechos, contenedor) no constituyen una etapa: atraviesan varias, según WP-0014.
- Las salidas "no inventariadas" (objetivos, escaleta, comentarios, contenedor) se señalan tal como las marca WP-0017 §4; no se crean activos nuevos.
- Todo deriva de WP-0012/0013/0014/0017; **no** se proponen estados, entidades, modelos ni arquitectura.

---

## 7. Referencias

- WP-0012 — YouTube Documentary Production Capability Map · `docs/research/YOUTUBE-DOCUMENTARY-PRODUCTION-CAPABILITY-MAP.md`
- WP-0013 — MVP Capability Inventory · `docs/research/MVP-CAPABILITY-INVENTORY.md`
- WP-0014 — Capability Dependency Map · `docs/research/CAPABILITY-DEPENDENCY-MAP.md`
- WP-0017 — MVP Capability Traceability Matrix · `docs/research/MVP-CAPABILITY-TRACEABILITY-MATRIX.md`

---

_Fin de la extracción. Documento derivado exclusivamente de WP-0012/0013/0014/0017: no propone estados del dominio, no define entidades, no crea un modelo de ciclo de vida, no infiere arquitectura y no modifica documentos existentes._
