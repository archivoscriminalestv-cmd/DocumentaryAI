"""Ventana principal de DocumentaryAI Studio V0.1 (DAS-001).

Contiene solo interfaz y llamadas a los servicios. Nada de lógica de negocio. Trabajo en
segundo plano vía QThreadPool para no bloquear la UI. Un QTimer refresca el estado cada pocos
segundos leyendo datos YA existentes (nunca recalcula).

Pestañas futuras (Dashboard, Investigación, Generación, …) se dejan preparadas pero deshabilitadas.
"""

import time

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.studio import STUDIO_BUILD, STUDIO_NAME, STUDIO_VERSION, config
from app.studio.services import LearningService, LogTail, StatusService

# Pestañas que existirán en el futuro (solo estructura; deshabilitadas en V0.1).
FUTURE_TABS = [
    "Dashboard", "Investigación", "Generación", "Storyboard", "Narrativa",
    "Chief Architect", "Backlog", "Knowledge Explorer", "CIE", "Backups",
    "Configuración", "APIs",
]
_REFRESH_MS = 3000


# --- trabajo en segundo plano ------------------------------------------------

class _Signals(QObject):
    done = Signal(object)
    error = Signal(str)


class _Task(QRunnable):
    def __init__(self, fn) -> None:
        super().__init__()
        self._fn = fn
        self.signals = _Signals()

    def run(self) -> None:  # pragma: no cover (hilo)
        try:
            self.signals.done.emit(self._fn())
        except Exception as exc:  # noqa: BLE001
            self.signals.error.emit(f"{type(exc).__name__}: {exc}")


def _fmt_runtime(seconds: int) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}h {m:02d}m {s:02d}s" if h else f"{m:d}m {s:02d}s"


class MainWindow(QMainWindow):
    def __init__(self, learning: LearningService | None = None,
                 status: StatusService | None = None) -> None:
        super().__init__()
        self._learning = learning or LearningService()
        self._status = status or StatusService(learning_service=self._learning)
        self._pool = QThreadPool.globalInstance()
        self._tail = LogTail(config.run_log_path())
        self._tailing = False
        self._last_learned = None
        self._was_learning = None

        self.setWindowTitle(f"{STUDIO_NAME} v{STUDIO_VERSION}")
        self.resize(760, 640)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addLayout(self._build_header())
        self._tabs = self._build_tabs()
        layout.addWidget(self._tabs, 1)

        self._timer = QTimer(self)
        self._timer.setInterval(_REFRESH_MS)
        self._timer.timeout.connect(self._refresh_status)
        self._timer.start()
        self._refresh_status()

    # ------------------------------------------------------------------ header
    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        left = QVBoxLayout()
        title = QLabel(STUDIO_NAME)
        f = QFont(); f.setPointSize(18); f.setBold(True)
        title.setFont(f)
        left.addWidget(title)
        self._subtitle = QLabel(f"v{STUDIO_VERSION} · build {STUDIO_BUILD} · Sistema: operativo")
        left.addWidget(self._subtitle)
        row.addLayout(left)
        row.addStretch(1)

        self._indicator = QLabel("⚪ Inactivo")
        fi = QFont(); fi.setPointSize(12); fi.setBold(True)
        self._indicator.setFont(fi)
        self._indicator.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self._set_indicator(False)
        row.addWidget(self._indicator)
        return row

    # ------------------------------------------------------------------ tabs
    def _build_tabs(self) -> QTabWidget:
        tabs = QTabWidget()
        tabs.addTab(self._build_learning_tab(), "Learning")
        for name in FUTURE_TABS:
            placeholder = QWidget()
            pl = QVBoxLayout(placeholder)
            lbl = QLabel(f"{name}\n\n(Próximamente)")
            lbl.setAlignment(Qt.AlignCenter)
            pl.addWidget(lbl)
            idx = tabs.addTab(placeholder, name)
            tabs.setTabEnabled(idx, False)
        return tabs

    def _build_learning_tab(self) -> QWidget:
        tab = QWidget()
        v = QVBoxLayout(tab)
        v.setSpacing(12)

        # Sección 1 — Learning: añadir URLs
        box1 = QGroupBox("Learning")
        b1 = QVBoxLayout(box1)
        self._btn_add = QPushButton("Añadir URLs")
        self._btn_add.clicked.connect(self._on_add_urls)
        b1.addWidget(self._btn_add)
        v.addWidget(box1)

        # Sección 2 — botón enorme de inicio
        self._btn_start = QPushButton("▶  Iniciar Aprendizaje")
        fs = QFont(); fs.setPointSize(16); fs.setBold(True)
        self._btn_start.setFont(fs)
        self._btn_start.setMinimumHeight(64)
        self._btn_start.clicked.connect(self._on_start_learning)
        v.addWidget(self._btn_start)

        # Sección 3 — estado en tiempo real (solo texto)
        box3 = QGroupBox("Estado")
        g = QVBoxLayout(box3)
        self._lbl_status = QLabel("—")
        self._lbl_status.setTextFormat(Qt.PlainText)
        self._lbl_status.setWordWrap(True)
        mono = QFont("Consolas"); mono.setStyleHint(QFont.Monospace)
        self._lbl_status.setFont(mono)
        g.addWidget(self._lbl_status)
        v.addWidget(box3)

        # Sección 4 — log de eventos importantes
        box4 = QGroupBox("Log")
        g4 = QVBoxLayout(box4)
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(500)
        g4.addWidget(self._log)
        v.addWidget(box4, 1)
        return tab

    # ------------------------------------------------------------------ acciones
    def _on_add_urls(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecciona un fichero .txt de URLs", "", "Texto (*.txt)")
        if not path:
            return
        self._btn_add.setEnabled(False)
        self._log_event(f"Cargando URLs desde: {path}")
        task = _Task(lambda: self._learning.add_urls(path))
        task.signals.done.connect(self._on_urls_added)
        task.signals.error.connect(self._on_worker_error)
        self._pool.start(task)

    def _on_urls_added(self, result) -> None:
        self._btn_add.setEnabled(True)
        if not result.ok:
            self._log_event(f"Error al cargar URLs: {result.error}")
            return
        self._log_event(
            f"Cola cargada — encontradas {result.found} · duplicadas {result.duplicates} · "
            f"añadidas {result.added} · errores {result.invalid}")

    def _on_start_learning(self) -> None:
        res = self._learning.start_learning()
        if res.already_running:
            self._log_event("DocumentaryAI ya está aprendiendo (no se lanza otro proceso)")
        elif res.started:
            self._tail.attach_end()          # seguir solo la salida de ESTA ejecución
            self._log_event("🟢 Aprendizaje iniciado")
        self._refresh_status()

    def _on_worker_error(self, msg: str) -> None:
        self._btn_add.setEnabled(True)
        self._log_event(f"Error: {msg}")

    # ------------------------------------------------------------------ estado
    def _refresh_status(self) -> None:
        snap = self._status.snapshot()
        self._set_indicator(snap.learning)

        current = snap.current_video or "—"
        self._lbl_status.setText(
            f"Documentales aprendidos : {snap.learned}\n"
            f"Pendientes              : {snap.pending}\n"
            f"Fallidos                : {snap.failed}\n"
            f"Horas aprendidas        : {snap.hours_learned:.2f} h\n"
            f"Planos                  : {snap.shots_analyzed}\n"
            f"Escenas                 : {snap.scenes}\n"
            f"Vídeo actual            : {current}\n"
            f"Tiempo de ejecución     : {_fmt_runtime(snap.runtime_seconds) if snap.learning else '—'}")

        # botón de inicio: deshabilitado mientras aprende
        self._btn_start.setEnabled(not snap.learning)
        self._btn_start.setText("Aprendizaje en ejecución" if snap.learning
                                else "▶  Iniciar Aprendizaje")

        # seguimiento del log del proceso (tail del fichero; nunca pipes de la UI)
        if snap.learning and not self._tailing:
            if self._was_learning is None:      # ya aprendía al abrir Studio → reconexión
                self._tail.attach_end()
                self._log_event("🟢 Aprendizaje activo (reconectado)")
            self._tailing = True
        if self._tailing:
            for line in self._tail.read_new():
                self._append_log_line(line)
        if not snap.learning and self._tailing:
            self._tailing = False

        # eventos importantes derivados de deltas (sin spam)
        if self._was_learning is True and snap.learning is False:
            self._log_event("Aprendizaje finalizado")
        if self._last_learned is not None and snap.learned > self._last_learned:
            self._log_event(f"Vídeo terminado (total aprendidos: {snap.learned})")
        self._was_learning = snap.learning
        self._last_learned = snap.learned

    def _set_indicator(self, learning: bool) -> None:
        if learning:
            self._indicator.setText("🟢 Modo Aprendizaje")
            self._indicator.setStyleSheet("color: #1a7f37;")
        else:
            self._indicator.setText("⚪ Inactivo")
            self._indicator.setStyleSheet("color: #6a737d;")

    # ------------------------------------------------------------------ util
    def _log_event(self, message: str) -> None:
        self._log.appendPlainText(f"[{time.strftime('%H:%M:%S')}] {message}")

    def _append_log_line(self, line: str) -> None:
        """Vuelca una línea cruda del proceso de aprendizaje (ya trae su propio formato)."""
        self._log.appendPlainText(line)
