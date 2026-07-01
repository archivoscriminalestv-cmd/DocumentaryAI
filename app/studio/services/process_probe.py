"""Detección de procesos (DAS-001) — saber si learn_queue está vivo.

Best-effort y multiplataforma, sin dependencias externas. El subprocess se usa SOLO aquí y en
LearningService (nunca repartido por la UI). Si algo falla, se degrada a "no lo sé" devolviendo
listas vacías / False, nunca lanza.
"""

import os
import subprocess
import sys

_LEARN_MARKER = "app.cli.learn_queue"
_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def pid_alive(pid: int) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        if os.name == "nt":
            out = subprocess.run(
                ["tasklist", "/FI", f"PID eq {int(pid)}", "/NH"],
                capture_output=True, text=True, creationflags=_NO_WINDOW, timeout=10)
            return str(pid) in (out.stdout or "")
        os.kill(int(pid), 0)   # POSIX: señal 0 = ¿existe?
        return True
    except (OSError, ValueError, subprocess.SubprocessError):
        return False


def find_learn_queue_pids() -> list[int]:
    """PIDs de procesos cuyo comando incluye ``app.cli.learn_queue`` (arrancados fuera de Studio)."""
    try:
        if os.name == "nt":
            out = subprocess.run(
                ["wmic", "process", "get", "ProcessId,CommandLine", "/format:list"],
                capture_output=True, text=True, creationflags=_NO_WINDOW, timeout=15)
            return _parse_wmic(out.stdout or "")
        out = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True, timeout=15)
        pids = []
        for line in (out.stdout or "").splitlines():
            if _LEARN_MARKER in line:
                head = line.strip().split(None, 1)
                if head and head[0].isdigit():
                    pids.append(int(head[0]))
        return pids
    except (OSError, subprocess.SubprocessError, ValueError):
        return []


def _parse_wmic(text: str) -> list[int]:
    pids: list[int] = []
    cmd_has_marker = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("CommandLine="):
            cmd_has_marker = _LEARN_MARKER in line
        elif line.startswith("ProcessId="):
            value = line.split("=", 1)[1].strip()
            if cmd_has_marker and value.isdigit() and int(value) != os.getpid():
                pids.append(int(value))
            cmd_has_marker = False
    return pids


def python_executable() -> str:
    return sys.executable or "python"
