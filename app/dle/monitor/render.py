"""Render del monitor (DLE-003).

``render(state)`` es una función PURA (estado → texto), por lo que es testeable de
forma determinista. ``LiveDisplay`` repinta el bloque en el sitio (ANSI) sin ensuciar
la terminal: sube el cursor y reescribe cada línea.
"""

import sys


def _fmt_time(seconds: float) -> str:
    seconds = int(max(0, seconds))
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02d}:{sec:02d}" if hours else f"{minutes}:{sec:02d}"


def _fmt_bytes(num: int) -> str:
    value = float(num)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} GB"


def _bar(fraction: float, width: int = 28) -> str:
    fraction = max(0.0, min(1.0, fraction))
    filled = int(round(fraction * width))
    return "#" * filled + "-" * (width - filled)


def render(state) -> str:
    s = state
    shot = f"{s.shot_index}/{s.shot_total}" if s.shot_total else "—"
    lines = [
        "== Live Learning Monitor ==========================",
        f" Documental : {s.doc_ref or '-'}",
        f" En cola    : {s.position}/{s.total}",
        f" Etapa      : {s.stage or '-'}",
        f" Plano      : {shot}",
        f" Escenas    : {s.scene_total or '-'}",
        f" Global     : [{_bar(s.global_percent)}] {s.global_percent * 100:5.1f}%",
        f" ETA        : {_fmt_time(s.eta)}   (transcurrido {_fmt_time(s.elapsed)})",
        f" Aprendidos : {s.docs_learned} doc  |  {s.hours_learned:.2f} h",
        f" KB size    : {_fmt_bytes(s.kb_size_bytes)}",
    ]
    if s.last_error:
        lines.append(f" Ultimo error: {s.last_error}")
    lines.append("===================================================")
    return "\n".join(lines)


class LiveDisplay:
    """Repinta el bloque en el sitio usando secuencias ANSI (sin scroll)."""

    def __init__(self, stream=None) -> None:
        self._stream = stream or sys.stdout
        self._lines = 0

    def update(self, text: str) -> None:
        out = self._stream
        if self._lines:
            out.write(f"\x1b[{self._lines}A")        # sube el cursor N líneas
        for line in text.split("\n"):
            out.write("\x1b[2K" + line + "\n")        # limpia la línea y escribe
        self._lines = text.count("\n") + 1
        try:
            out.flush()
        except Exception:
            pass
