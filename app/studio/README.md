# DocumentaryAI Studio (DAS-001)

El **Shell oficial de escritorio** de DocumentaryAI. A partir de aquí, toda interacción podrá
hacerse desde Studio (la CLI sigue existiendo para automatización y testing). V0.1 es
deliberadamente pequeña, pero con una arquitectura preparada para crecer.

## Principio arquitectónico

> Studio **nunca** contiene lógica de negocio. Solo **orquesta** los motores existentes.

```
Studio (UI, PySide6)
   └── services/  (LearningService, StatusService)   ← única capa que Studio conoce
          └── CLIs existentes (queue_add, learn_queue)
                 └── motores (DLE, …)
```

- La UI solo habla con **servicios**. Los servicios llaman a las **CLIs/motores existentes**.
- No se reimplementa `queue_add` ni `learn_queue`: se **usan**.
- Los servicios (`app.studio.services`) están **libres de Qt** y son testeables sin pantalla; la
  UI (`app.studio.ui`) importa **PySide6 de forma perezosa**.
- No se modifica ningún motor. Todo por composición.

## Pantalla principal (V0.1)

- **Header:** nombre, versión/build, estado del sistema, y en la esquina superior derecha un
  **indicador**: `🟢 Modo Aprendizaje` / `⚪ Inactivo`.
- **Sección 1 · Learning:** botón **[ Añadir URLs ]** → selector de fichero `.txt` → llama al
  flujo existente `queue_add` → muestra en el log: encontradas / duplicadas / añadidas / errores.
- **Sección 2:** botón grande **▶ Iniciar Aprendizaje** → lanza exactamente
  `python -m app.cli.learn_queue` en segundo plano, sin abrir consola, sin bloquear la UI. Si ya
  se está aprendiendo, se **deshabilita** y muestra "Aprendizaje en ejecución".
- **Sección 3 · Estado (solo texto, refresco cada 3 s):** documentales aprendidos, pendientes,
  fallidos, horas, planos, escenas, vídeo actual y tiempo de ejecución. Consume datos ya
  existentes; **nunca recalcula**.
- **Sección 4 · Log:** caja desplazable con eventos importantes (cola cargada, aprendizaje
  iniciado, vídeo terminado, error, aprendizaje finalizado). Sin miles de líneas.

## Detección de aprendizaje en curso

`LearningService` sabe si `learn_queue` ya está corriendo — lo arrancara Studio o se arrancara
desde fuera (VS Code):

1. **Lock de sesión** `output/studio/learning.lock` (PID + inicio) escrito por Studio; si el PID
   sigue vivo → aprendiendo. Si el PID murió → lock obsoleto, se limpia.
2. **Sonda de procesos** (best-effort, multiplataforma) que busca `app.cli.learn_queue` en los
   procesos vivos → detecta ejecuciones externas.

Si ya está aprendiendo, Studio **no lanza otro** y lo indica claramente. El indicador
`🟢 Modo Aprendizaje` permite saber de un vistazo que el DLE está trabajando y que **no se deben
tocar esos motores**.

## Proceso de aprendizaje 100 % invisible (DAS-001A)

El aprendizaje se lanza como proceso de fondo **sin ninguna ventana** y sin robar el foco: se
puede seguir usando el ordenador (VS Code, escribir, navegar) durante horas mientras aprende.

- **Causa raíz corregida:** antes se usaba `CREATE_NO_WINDOW | DETACHED_PROCESS`. `DETACHED_PROCESS`
  deja a `learn_queue` **sin consola**; al lanzar el DLE después `yt-dlp.exe`/`ffmpeg.exe` (apps de
  consola, sin flags), Windows les asigna **una consola nueva y visible a cada uno** → ventanas que
  parpadean. La solución es **`CREATE_NO_WINDOW` a secas** (`win_creationflags()`): el hijo tiene una
  consola **oculta** que todos los nietos heredan → cero ventanas. Se añade `STARTUPINFO` con
  `SW_HIDE` como defensa en profundidad.
- **Salida capturada, no ventanas:** la salida se redirige al fichero de log de la sesión
  (`output/studio/learning_run.log`) y Studio la muestra en su **Log** haciendo *tail* del fichero
  (`LogTail`). No se usan pipes propiedad de la UI, para que el proceso **sobreviva al cierre de
  Studio**.
- **Reconexión:** si cierras Studio con el aprendizaje en marcha, al reabrir se detecta por PID
  (`learning.lock` + sonda de procesos), muestra `🟢 Aprendizaje activo (reconectado)` y retoma el
  *tail* del log — **sin lanzar un segundo proceso**.

## Ejecutar

```bash
pip install PySide6          # única dependencia extra de Studio
python -m app.studio
```

Si PySide6 no está instalado, `python -m app.studio` no falla con un traceback: muestra las
instrucciones de instalación.

## Empaquetado (futuro)

Preparado para generar **«DocumentaryAI Studio.exe»** con PyInstaller:

```bash
pip install pyinstaller PySide6
pyinstaller app/studio/packaging/DocumentaryAI-Studio.spec
```

El aprendizaje (torch/whisper) corre en un **proceso aparte** (`learn_queue`), por lo que el
ejecutable de Studio se mantiene ligero.

## Estructura

```
app/studio/
  __init__.py          nombre / versión / build
  config.py            rutas (raíz, knowledge, lock, log)
  __main__.py          python -m app.studio (mensaje amable si falta PySide6)
  services/            LÓGICA de orquestación (sin Qt)
    models.py          QueueAddResult / LearningState / StartResult / StatusSnapshot
    process_probe.py   pid_alive + búsqueda de learn_queue (sin dependencias)
    learning_service.py add_urls (usa queue_add) · start_learning (subprocess) · detección
    status_service.py  lee learning_statistics.json + learning_queue.json (no recalcula)
  ui/                  INTERFAZ (PySide6, import perezoso)
    app.py             QApplication
    main_window.py     header + secciones + indicador + pestañas futuras (deshabilitadas)
  packaging/           DocumentaryAI-Studio.spec (PyInstaller)
```

## Futuro (solo estructura preparada, no implementado)

Pestañas: Dashboard · Investigación · Generación · Storyboard · Narrativa · Chief Architect ·
Backlog · Knowledge Explorer · CIE · Backups · Configuración · APIs.

Ver `docs/adr/ADR-0029-DocumentaryAI-Studio.md`.
