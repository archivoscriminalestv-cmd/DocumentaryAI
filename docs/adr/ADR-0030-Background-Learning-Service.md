# ADR-0030 — Background Learning Service (invisible process)

- **Status:** Accepted
- **Date:** 2026-07-01
- **Sprint:** DAS-001A (bug fix + arquitectura sobre DAS-001)
- **Relates:** ADR-0029 (DocumentaryAI Studio)

## Contexto

En la validación real de Studio V0.1, iniciar el aprendizaje abría continuamente ventanas de
consola (yt-dlp/ffmpeg) que robaban el foco y hacían inusable el ordenador durante horas.
Ejecutar exactamente `python -m app.cli.learn_queue` desde VS Code **no** reproduce el problema,
así que el bug era exclusivo de **cómo Studio lanzaba el proceso**, no del DLE ni de learn_queue.

## Causa raíz (demostrada, no asumida)

`LearningService._default_spawn` usaba `creationflags = CREATE_NO_WINDOW | DETACHED_PROCESS`.
Prueba empírica (probe `GetConsoleCP`, que devuelve 0 solo si el proceso no tiene consola):

| creationflags | ¿hijo con consola? | efecto en yt-dlp/ffmpeg (nietos) |
|---|---|---|
| `CREATE_NO_WINDOW` | **SÍ** (oculta) | la heredan → sin ventana |
| `DETACHED_PROCESS` | **NO** | consola nueva **visible** por cada nieto |
| `CREATE_NO_WINDOW \| DETACHED_PROCESS` (bug) | **NO** | consola nueva **visible** por cada nieto |

`DETACHED_PROCESS` **anula** a `CREATE_NO_WINDOW` y deja a `learn_queue` sin consola. Como el DLE
lanza yt-dlp/ffmpeg (apps de consola) sin flags, al no haber consola que heredar Windows crea una
**consola nueva y visible** para cada nieto. Verificado además a nivel de nieto: con el flag
antiguo el nieto abre `VENTANA_VISIBLE`; con el nuevo, `sin_ventana`.

## Decisión

1. **`win_creationflags()` = `CREATE_NO_WINDOW` a secas** (sin `DETACHED_PROCESS`). El hijo tiene
   una consola oculta que todos los nietos heredan → proceso 100 % invisible, sin robo de foco.
   El hijo sobrevive igual al cierre de Studio (Windows no mata a los hijos al terminar el padre),
   por lo que la reconexión por PID se mantiene.
2. **`win_startupinfo()` con `STARTF_USESHOWWINDOW` + `SW_HIDE`** como defensa en profundidad.
3. **Salida por fichero + `LogTail`, no pipes de la UI.** learn_queue redirige stdout/stderr al
   log de sesión (`output/studio/learning_run.log`); Studio muestra el progreso haciendo *tail*
   incremental de ese fichero en su Log. Se descartan pipes propiedad de la UI porque morirían al
   cerrar Studio (rompiendo la independencia del proceso) — el fichero es la opción profesional
   para un servicio de fondo que debe sobrevivir a la UI.
4. **Reconexión robusta:** al abrir Studio, si hay aprendizaje vivo (lock + PID / sonda), muestra
   `🟢 Aprendizaje activo (reconectado)` y hace `attach_end()` del log (sin volcar el histórico),
   sin lanzar un segundo proceso.

## Alcance

Todo el cambio vive dentro de `app/studio/`. **No** se modifica DLE, YIE, DKS, VIS, VAI, Composer,
NAR, KBG, PCX, DCA, AIM, INF, el pipeline ni `learn_queue`. Arquitectura por composición.

## Consecuencias

- **Positivo:** el aprendizaje es invisible; el usuario trabaja con normalidad; Studio muestra el
  progreso en su propio Log; reconexión fiable; sin hacks/sleeps/batch/powershell auxiliares. Fix
  correcto en el origen, no un parche del síntoma.
- **Limitaciones aceptadas:** el detalle del progreso mostrado depende de lo que imprima el DLE
  (no se modifica); el *tail* se refresca al ritmo del temporizador de la UI (3 s).

## Prueba

`win_creationflags()` = `0x08000000` sin bit `0x08` (test). Prueba de nieto real: antiguo →
`VENTANA_VISIBLE`; nuevo → `sin_ventana`. Tests `tests/test_studio.py` 20/20 (incl. flags,
STARTUPINFO oculto y `LogTail` incremental/attach_end/truncado). UI construye offscreen (PySide6
6.11.1).
