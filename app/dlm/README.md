# DLM — Documentary Learning Monitor & Dashboard

**Centro de control** del aprendizaje de DocumentaryAI. Permite dejar el sistema
aprendiendo durante horas o días y comprobar de un vistazo, en tiempo real, qué se está
aprendiendo, cuánto falta, qué motores funcionan, si algo falla y cómo crece el corpus.

**100% aditivo y por composición.** No modifica DLE/Queue/YIE/DKS/VIS/VAI/VSC/VPL/
Composer/FFmpeg ni inspecciona su estado interno: solo consume los **eventos públicos**
(`ProgressEvent`, DLE-003) y lee los **artefactos públicos** de `knowledge/`.

```
ProgressEvent (público)  →  DashboardMonitor  →  DashboardState  →  TerminalDashboardRenderer
knowledge/*.json (público) ↗                                       (ANSI o fallback limpio)
```

## Módulos (`app/dlm/`)

| Módulo | Responsabilidad |
|--------|-----------------|
| `models.py` | `DashboardState`, `CurrentDocument`, `CorpusStatistics`, `GlobalStatistics`, `EngineHealth`, `HealthStatus` |
| `monitor.py` | `DashboardMonitor` — compone `LearningMonitor` (DLE-003) y añade salud de motores, throughput, eventos, errores, stats del vídeo |
| `statistics.py` | `ThroughputCalculator`, `ETAEstimator`, `SpeedEstimator` (reloj inyectable, deterministas) |
| `renderer.py` | `TerminalDashboardRenderer`, `render_dashboard`, `ProgressBar`, `TableRenderer` (ANSI + fallback) |
| `persistence.py` | `dashboard_history.json` (acumulativo) + `session_statistics.json` |

## Qué muestra

Corpus (documentales/horas/planos/escenas/tamaño/vídeos) · Cola (posición/total) · Vídeo
actual (id/etapa/plano) · Progreso (barra + % + ETA + tiempo + vídeos/hora) · **Salud de
motores** (RUNNING/WAITING/FINISHED/FAILED/SKIPPED, nunca ambiguo) · Estadísticas del vídeo
actual (de `knowledge/<id>/statistics.json` al terminar) · Throughput (planos/min,
escenas/min, MB conocimiento/hora) · Últimos eventos · Errores. Al terminar: **Learning
Finished** con el resumen.

## Salud de motores (honesto)

Los eventos públicos son por **etapa** (downloading/analyzing/learning/storing), no por
motor individual. El dashboard mapea cada motor a la etapa que lo ejercita y deriva su
estado de la etapa alcanzada por el documental actual: etapa anterior → FINISHED, actual →
RUNNING, posterior → WAITING; fallo → FAILED en la etapa activa. Es la granularidad real
disponible sin inspeccionar internals.

## Terminal

ANSI cuando se puede (Windows Terminal / PowerShell / VSCode / CMD moderno): reutiliza la
misma pantalla (`clear`+`home`), sin imprimir miles de líneas. **Fallback limpio** cuando
no hay ANSI (no TTY): imprime el bloque. `render_dashboard(state)` devuelve el texto puro
(determinista) — usado por los tests.

## CLI

```bash
python -m app.cli.learn_dashboard                 # Dashboard + Queue + YIE + DLE + resumen
python -m app.cli.learn_dashboard --limit 50
```

Un único comando: arranca el dashboard, procesa la cola (con YIE→DLE), persiste
`dashboard_history.json` / `session_statistics.json` y muestra el resumen final.

## Decisión arquitectónica

Ver `docs/adr/ADR-0013-Learning-Dashboard-and-Live-Monitoring.md`.

## Notas honestas

- Salud por etapa (no por motor): es lo que permiten los eventos públicos.
- Campos del corpus sin señal pública (canales/views/likes/comments) se muestran a 0 hasta
  que exista un artefacto público que los aporte (no se inventan).
- Determinista: mismos eventos + mismo reloj inyectable → mismo estado y mismo render.
