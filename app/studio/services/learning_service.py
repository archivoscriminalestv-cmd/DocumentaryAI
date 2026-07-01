"""LearningService (DAS-001) — orquesta el aprendizaje SIN reimplementar nada.

- Añadir URLs: usa el flujo EXISTENTE ``app.cli.queue_add`` (no se duplica queue_add).
- Iniciar aprendizaje: lanza EXACTAMENTE ``python -m app.cli.learn_queue`` como proceso en
  segundo plano, sin abrir consola y sin bloquear la UI. Un único punto de subprocess.
- Detección: si learn_queue ya está en marcha (por Studio o desde fuera), NO lanza otro y lo
  indica. Esto permite saber que "DocumentaryAI está aprendiendo" y no tocar esos motores.

Todas las dependencias externas (spawn, reloj, sonda de procesos, queue_add) son inyectables
para poder testear sin lanzar procesos reales.
"""

import json
import os
import subprocess
import time

from app.studio import config
from app.studio.services import process_probe
from app.studio.services.models import LearningState, QueueAddResult, StartResult

_CREATE_NO_WINDOW = 0x08000000                              # consola SIN ventana (se hereda)


def win_creationflags() -> int:
    """Flags de creación en Windows para un proceso de fondo verdaderamente invisible.

    CAUSA RAÍZ del bug DAS-001 (demostrada): se usaba ``CREATE_NO_WINDOW | DETACHED_PROCESS``.
    DETACHED_PROCESS deja al hijo (learn_queue) SIN consola; cuando el DLE lanza después
    yt-dlp.exe / ffmpeg.exe (apps de consola, sin flags), Windows le asigna una CONSOLA NUEVA
    y VISIBLE a cada uno → ventanas que parpadean y roban el foco.

    Con ``CREATE_NO_WINDOW`` a secas el hijo SÍ tiene consola (oculta), que los nietos heredan
    → cero ventanas. NO se combina con DETACHED_PROCESS (lo anularía). El hijo sobrevive al
    cierre de Studio igualmente (Windows no mata a los hijos al terminar el padre)."""
    return _CREATE_NO_WINDOW if os.name == "nt" else 0


def win_startupinfo():
    """STARTUPINFO con SW_HIDE (defensa en profundidad; no abre ninguna ventana propia)."""
    if os.name != "nt":
        return None
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    return si


def _default_spawn(cmd: list[str], cwd: str, log_path: str) -> int:
    """Lanza learn_queue en segundo plano, 100% invisible, capturando su salida en un fichero.

    La salida se REDIRIGE al log de la sesión (no a pipes propiedad de la UI): así el proceso
    es independiente de Studio —sobrevive a su cierre— y Studio muestra el progreso haciendo
    *tail* de ese fichero (ver LogTail). Nunca aparece una consola ni una ventana."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    log = open(log_path, "a", encoding="utf-8", errors="replace")
    kwargs = {"cwd": cwd, "stdout": log, "stderr": subprocess.STDOUT,
              "stdin": subprocess.DEVNULL, "close_fds": True}
    if os.name == "nt":
        kwargs["creationflags"] = win_creationflags()
        kwargs["startupinfo"] = win_startupinfo()
    else:
        kwargs["start_new_session"] = True
    proc = subprocess.Popen(cmd, **kwargs)
    return proc.pid


class LearningService:
    def __init__(self, root: str | None = None, *, spawn=None, clock=None, probe=None,
                 queue_add_run=None) -> None:
        self._root = config.project_root(root)
        self._spawn = spawn or _default_spawn
        self._clock = clock or time.time
        self._probe = probe or process_probe.find_learn_queue_pids
        self._pid_alive = process_probe.pid_alive
        self._queue_add_run = queue_add_run          # None → import perezoso del flujo real

    # ------------------------------------------------------------------ URLs
    def add_urls(self, txt_path: str) -> QueueAddResult:
        """Delega en el flujo EXISTENTE queue_add. No reimplementa el parseo/dedup."""
        run = self._queue_add_run
        if run is None:
            from app.cli.queue_add import run as run  # import perezoso: sin dependencias pesadas
        try:
            res = run([txt_path], show_environment=False)
        except Exception as exc:                      # noqa: BLE001 (la UI nunca debe romperse)
            return QueueAddResult(source=txt_path, ok=False, error=f"{type(exc).__name__}: {exc}")
        return QueueAddResult(
            source=txt_path,
            found=int(res.get("found", 0)),
            added=int(res.get("added", 0)),
            duplicates=int(res.get("duplicates", 0)),
            invalid=int(res.get("invalid", 0)),
            ok=True)

    # ------------------------------------------------------------------ estado
    def learning_state(self) -> LearningState:
        lock = self._read_lock()
        if lock:
            pid = int(lock.get("pid", 0) or 0)
            if self._pid_alive(pid):
                started = float(lock.get("started_at", 0.0) or 0.0)
                runtime = max(0, int(self._clock() - started)) if started else 0
                return LearningState(running=True, pid=pid,
                                     source=str(lock.get("source", "studio")),
                                     started_at=started, runtime_seconds=runtime)
            self._clear_lock()                        # lock obsoleto: el proceso murió
        for pid in self._probe():                     # arrancado fuera de Studio
            return LearningState(running=True, pid=pid, source="external")
        return LearningState(running=False, source="none")

    def is_learning(self) -> bool:
        return self.learning_state().running

    # ------------------------------------------------------------------ lanzar
    def start_learning(self) -> StartResult:
        state = self.learning_state()
        if state.running:
            return StartResult(started=False, already_running=True, state=state,
                               message="DocumentaryAI ya está aprendiendo")
        cmd = [process_probe.python_executable(), "-u", "-m", "app.cli.learn_queue"]
        pid = self._spawn(cmd, self._root, config.run_log_path(self._root))
        started_at = float(self._clock())
        self._write_lock({"pid": int(pid), "started_at": started_at, "source": "studio",
                          "cmd": " ".join(cmd)})
        return StartResult(started=True, state=LearningState(
            running=True, pid=int(pid), source="studio", started_at=started_at, runtime_seconds=0),
            message="Aprendizaje iniciado")

    # ------------------------------------------------------------------ lock
    def _read_lock(self) -> dict | None:
        path = config.lock_path(self._root)
        if not os.path.exists(path):
            return None
        try:
            with open(path, encoding="utf-8") as h:
                return json.load(h)
        except (OSError, ValueError):
            return None

    def _write_lock(self, data: dict) -> None:
        path = config.lock_path(self._root)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as h:
            json.dump(data, h, ensure_ascii=False, indent=2, sort_keys=True)

    def _clear_lock(self) -> None:
        try:
            os.remove(config.lock_path(self._root))
        except OSError:
            pass
