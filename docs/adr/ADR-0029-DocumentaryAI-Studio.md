# ADR-0029 — DocumentaryAI Studio (Desktop Application Foundation)

- **Status:** Accepted
- **Date:** 2026-07-01
- **Sprint:** DAS-001
- **Relates:** ADR-0010 (DLE storage policy), DLE-002 (learning queue), ADR-0028 (Infrastructure
  Protection), ADR-0027 (Architectural Backlog)

## Contexto

DocumentaryAI había dejado de ser un conjunto de scripts y necesitaba un **shell oficial de
escritorio** desde el que operar sin depender de PowerShell. En particular, arrancar el
aprendizaje (`learn_queue`) desde una terminal es frágil (se pierde al cerrar la sesión) y no hay
forma visual de saber si el DLE está trabajando.

## Decisión 1 — Un shell de escritorio, no un frontend temporal

Se crea `app/studio/` como **subsistema independiente**: DocumentaryAI Studio. Es la interfaz
oficial (la CLI permanece para automatización/testing). V0.1 es mínima pero con arquitectura
para crecer (pestañas futuras ya previstas: Dashboard, Investigación, Generación, Storyboard,
Narrativa, Chief Architect, Backlog, Knowledge Explorer, CIE, Backups, Configuración, APIs).

## Decisión 2 — PySide6 / Qt, escritorio real (nada de web)

Se usa **PySide6 (Qt)**: aplicación de escritorio nativa, empaquetable como
«DocumentaryAI Studio.exe» (PyInstaller spec incluido). Sin Electron, sin HTML/React, sin
navegador. Estabilidad y mantenibilidad por encima de estética.

## Decisión 3 — Studio no contiene lógica de negocio; orquesta por composición

```
UI  →  services (LearningService/StatusService)  →  CLIs existentes  →  motores
```

Studio **no reimplementa** `queue_add` ni `learn_queue`: los **usa**. No se modifica ningún motor
(DLE/VIS/VAI/Composer/KBG/DCA/AIM/NAR/PCX/ECE) ni ningún pipeline. Los **servicios están libres
de Qt** (testeables sin pantalla) y la **UI importa PySide6 de forma perezosa**, de modo que el
resto del proyecto y los tests no dependen de un entorno gráfico.

## Decisión 4 — Un único punto de subprocess; aprendizaje en proceso aparte

`LearningService` es el **único** lugar que lanza procesos. «▶ Iniciar Aprendizaje» ejecuta
exactamente `python -m app.cli.learn_queue` como proceso en segundo plano, **sin ventana de
consola** (CREATE_NO_WINDOW/detached en Windows; `start_new_session` en POSIX) y sin bloquear la
UI. Correr el aprendizaje (torch/whisper) fuera del proceso de la UI protege la estabilidad de
Studio y mantiene ligero el futuro ejecutable.

## Decisión 5 — Detección fiable de "está aprendiendo" + indicador

Studio detecta si `learn_queue` ya corre por dos vías: (1) un **lock de sesión**
`output/studio/learning.lock` (PID + inicio) que Studio escribe y limpia si el PID muere, y
(2) una **sonda de procesos** best-effort que encuentra `learn_queue` aunque se arranque desde
fuera (VS Code). Si ya está aprendiendo, **no se lanza otro** y el botón se deshabilita. Un
**indicador** en la esquina superior derecha muestra `🟢 Modo Aprendizaje` / `⚪ Inactivo`: de un
vistazo se sabe si el DLE está trabajando (y, por tanto, que no deben tocarse esos motores).

## Decisión 6 — El estado se lee, no se recalcula

`StatusService` consume los datos **ya existentes** (`knowledge/learning_statistics.json` y
`knowledge/learning_queue.json`); nunca recalcula estadísticas ni importa motores pesados. Solo
texto: aprendidos, pendientes, fallidos, horas, planos, escenas, vídeo actual y tiempo de
ejecución.

## Consecuencias

- **Positivo:** se puede aprender documentales con doble clic, sin PowerShell; el indicador
  `🟢/⚪` da visibilidad inmediata del estado del DLE; arquitectura limpia y ampliable por
  pestañas; cero riesgo para los motores (composición pura); servicios totalmente testeables sin
  Qt (13/13, +1 test de UI que se omite si falta PySide6).
- **Limitaciones aceptadas (V0.1):** una sola pestaña funcional (Learning); las demás quedan como
  estructura deshabilitada; el ejecutable no se construye en este sprint (spec preparado); la
  sonda externa de procesos es best-effort; PySide6 es una dependencia opcional que el usuario
  instala (`pip install PySide6`).
```
DocumentaryAI Studio v0.1                                   🟢 Modo Aprendizaje
Learning · [ Añadir URLs ]
▶ Iniciar Aprendizaje
Estado: aprendidos 97 · pendientes 31 · horas 49.09 · planos 31884 · vídeo actual bbb
Log: Cola cargada — encontradas 128 · duplicadas 97 · añadidas 31 · errores 0
```
