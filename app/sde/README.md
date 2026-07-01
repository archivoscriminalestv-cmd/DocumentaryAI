# SDE — Shot Diversity Engine

Director de Fotografía **determinista**. Garantiza que cada plano tenga una composición
cinematográfica diferente **cuando la narrativa lo permite**, recordando todos los planos
ya rodados. Convierte un `ShotExecutionRequest` (VAI) en otro **enriquecido**.

No genera imágenes, no escribe prompts completos, no llama al VPL, no toca Motion ni
Composer. Único punto de integración:

```
VIS → VAI → SDE → VSC
```

**100% determinista:** sin `random` y sin dependencia del proveedor de imágenes. El mismo
documental produce siempre el mismo plan visual. Todas las decisiones se basan en reglas,
historial y contexto narrativo, y **siempre se justifican**.

## Módulos (`app/sde/`)

| Módulo | Responsabilidad |
|--------|-----------------|
| `models.py` | Vocabulario (shot size/ángulo/altura/lente/composición/posición/mirada/luz/movimiento), `ShotFingerprint`, `ShotRecord` |
| `history.py` | `ShotHistory`: memoria del documental + LRU por dimensión |
| `scoring.py` | Diversidad determinista (similitud ponderada, 0..1) |
| `rules.py` | Clasificación narrativa, parseo VAI→fingerprint, render fingerprint→spec |
| `planner.py` | `DiversityPlanner`: elige alternativas por LRU (sin azar) y las justifica |
| `continuity.py` | Salvaguardas: identidad y look de escena nunca cambian |
| `orchestrator.py` | `ShotDiversityEngine` (VAI→SDE→VSC) + `SDEContext` + estadísticas |
| `persistence.py` | `shot_history.json` + `shot_diversity_report.md` |

## Cómo decide (sin aleatoriedad)

1. **Parsea** el plano del VAI a un `ShotFingerprint` (tamaño, ángulo, lente, composición…).
2. **Clasifica la narrativa** (entrevista→continuidad; intimate/observational/reflective→
   diversidad moderada; reconstrucción/recurso→máxima; chase→dinamismo). Cada modo define
   qué dimensiones son **libres**.
3. Para cada dimensión libre, si su valor base ya apareció en los últimos N planos, elige
   la alternativa **menos usada recientemente** (LRU), desempatando por el orden del
   catálogo. Decisión reproducible y justificada.
4. **Verifica** que identidad y escena no cambian, **renderiza** a `camera_language` /
   `composition` (campos que el VSC ya consume) y **registra** el plano en el historial.

## Qué puede y qué no puede cambiar

- **Puede:** shot size, ángulo, altura, lente, composición, posición del sujeto, mirada,
  movimiento.
- **Nunca:** edad, aspecto, ropa, identidad del personaje (CCE), ni la continuidad de
  escena (localización, paleta, hora, clima, luz). Garantizado por `continuity.py`.

## Conciencia narrativa, de personaje y de escena

- **Narrativa:** no todo debe ser diferente; una entrevista mantiene continuidad, un plano
  recurso tiene libertad total.
- **Personaje:** el SDE solo toca encuadre/cámara; jamás la identidad.
- **Escena:** varía la composición dentro de la escena (evita repetir), preservando el look
  de continuidad (que es de escena, no de plano).

## Persistencia / informe

`shot_history.json` (todos los planos + decisiones) y `shot_diversity_report.md`
(diversidad media, repeticiones, variaciones aplicadas, distribuciones de tamaño/lente/
composición/ángulo/altura, y la tabla de decisiones por plano).

## Decisiones arquitectónicas

Ver `docs/adr/ADR-0005-Deterministic-Cinematographic-Diversity.md`.

## Resultado (documental Coquito, 26 planos)

| | Antes del SDE | Después del SDE |
|---|---|---|
| Composiciones distintas | 9 | **26** |
| Diversidad media | 0.21 | **0.75** |
| Lentes / tamaños / ángulos / alturas | repetidos | repartidos por todo el catálogo |
| Identidad del personaje | — | **intacta** |
| VPL / ALR | — | **sin cambios** |
