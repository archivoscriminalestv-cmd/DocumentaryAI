"""Render del dashboard en terminal (ANSI cuando se puede; fallback limpio si no).

``render_dashboard(state)`` devuelve el texto COMPLETO (determinista, sin códigos ANSI)
— ideal para tests. ``TerminalDashboardRenderer`` se encarga de pintar en pantalla,
reutilizando la MISMA pantalla con ANSI (clear+home) o, si no hay ANSI, imprimiendo el
bloque (fallback). Funciona en Windows Terminal / PowerShell / VSCode / CMD.
"""

import os
import sys

from app.dlm.models import DashboardState

_W = 51
_RULE = "=" * _W


def supports_ansi(stream=None) -> bool:
    stream = stream or sys.stdout
    if not hasattr(stream, "isatty") or not stream.isatty():
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    if os.name != "nt":
        return True
    # Windows: terminales modernos exponen estas variables.
    return bool(os.environ.get("WT_SESSION") or os.environ.get("TERM")
                or "vscode" in os.environ.get("TERM_PROGRAM", "").lower()
                or os.environ.get("ANSICON"))


class ProgressBar:
    @staticmethod
    def render(percent: float, width: int = 22) -> str:
        percent = max(0.0, min(1.0, percent))
        filled = int(round(percent * width))
        return "█" * filled + "░" * (width - filled)


class TableRenderer:
    @staticmethod
    def two_col(rows: list[tuple[str, str]], pad: int = 26) -> list[str]:
        return [f"{k:<{pad}} {v}" for k, v in rows]


def _section(title: str) -> list[str]:
    return [_RULE, title]


def _fmt_time(seconds: float) -> str:
    seconds = int(max(0, seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def render_dashboard(state: DashboardState) -> str:
    c, cur, g = state.corpus, state.current, state.globals
    lines: list[str] = [_RULE, "DOCUMENTARY AI — Learning Dashboard", _RULE]

    lines += _section("Corpus")
    lines += TableRenderer.two_col([
        ("Documentales aprendidos", str(c.documentaries)),
        ("Horas analizadas", f"{c.hours:.2f}"),
        ("Planos", str(c.shots)),
        ("Escenas", str(c.scenes)),
        ("Tamaño Knowledge", f"{c.knowledge_bytes / (1024 * 1024):.2f} MB"),
        ("Vídeos", str(c.videos)),
    ])

    lines += _section("Cola")
    lines += TableRenderer.two_col([
        ("En cola", str(state.queue_total)),
        ("Procesando", f"{state.queue_position} / {state.queue_total}"),
    ])

    lines += _section("Vídeo actual")
    lines += TableRenderer.two_col([
        ("Documental", cur.doc_id or cur.doc_ref or "—"),
        ("Etapa", cur.stage or "—"),
        ("Plano", f"{cur.shot_index}/{cur.shot_total}" if cur.shot_total else "—"),
    ])

    lines += _section("Progreso")
    lines.append(f"{ProgressBar.render(g.global_percent)}  {g.global_percent * 100:.0f} %")
    lines += TableRenderer.two_col([
        ("ETA cola", _fmt_time(g.eta_queue)),
        ("Tiempo transcurrido", _fmt_time(g.elapsed)),
        ("Vídeos / hora", f"{g.videos_per_hour:.2f}"),
        ("Horas vídeo / hora", f"{g.video_hours_per_hour:.2f}"),
    ])

    lines += _section("Estado de motores")
    for e in state.engines:
        lines.append(f"  [{_status_mark(e.status)}] {e.name:<24} {e.status}")

    lines += _section("Estadísticas del vídeo actual")
    lines += TableRenderer.two_col([
        ("Planos detectados", str(cur.shot_total or "—")),
        ("Escenas", str(cur.scene_total or "—")),
        ("Duración media plano", f"{cur.avg_shot_length:.2f}" if cur.avg_shot_length else "—"),
        ("Cuts/min", f"{cur.cuts_per_minute:.2f}" if cur.cuts_per_minute else "—"),
        ("Movimiento dominante", cur.dominant_movement),
        ("Temperatura color", cur.dominant_color_temperature),
        ("Audio (s)", f"{cur.audio_seconds:.1f}" if cur.audio_seconds else "—"),
        ("Narración (s)", f"{cur.narration_seconds:.1f}" if cur.narration_seconds else "—"),
    ])

    lines += _section("Throughput")
    lines += TableRenderer.two_col([
        ("Planos / min", f"{g.shots_per_minute:.2f}"),
        ("Escenas / min", f"{g.scenes_per_minute:.2f}"),
        ("MB conocimiento / hora", f"{g.knowledge_mb_per_hour:.2f}"),
        ("Completados / Fallidos", f"{g.completed} / {g.failed}"),
    ])

    lines += _section("Últimos eventos")
    lines += [f"  {e}" for e in state.last_events] or ["  —"]

    lines += _section("Errores")
    lines += [f"  {e}" for e in state.errors[-5:]] or ["  (ninguno)"]
    lines.append(_RULE)
    if state.finished:
        lines.append("Learning Finished")
        lines.append(_RULE)
    return "\n".join(lines)


def _status_mark(status: str) -> str:
    return {"RUNNING": "~", "WAITING": " ", "FINISHED": "Y", "FAILED": "X", "SKIPPED": "-"}.get(status, "?")


class TerminalDashboardRenderer:
    def __init__(self, stream=None, ansi: bool | None = None) -> None:
        self._stream = stream or sys.stdout
        self._ansi = supports_ansi(self._stream) if ansi is None else ansi

    def render(self, state: DashboardState) -> None:
        text = render_dashboard(state)
        if self._ansi:
            self._stream.write("\x1b[2J\x1b[H")     # limpia pantalla + cursor arriba
            self._stream.write(text + "\n")
        else:
            self._stream.write(text + "\n\n")        # fallback: bloque (se desplaza)
        try:
            self._stream.flush()
        except Exception:
            pass
