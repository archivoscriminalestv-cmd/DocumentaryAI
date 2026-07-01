"""Arranque de la aplicación Qt (DAS-001).

`run()` crea la QApplication y muestra la ventana principal. Se importa PySide6 aquí (no antes)
para que el resto del subsistema funcione sin Qt.
"""

import sys


def run(argv: list[str] | None = None) -> int:
    from PySide6.QtWidgets import QApplication

    from app.studio import STUDIO_NAME
    from app.studio.ui.main_window import MainWindow

    app = QApplication(argv if argv is not None else sys.argv)
    app.setApplicationName(STUDIO_NAME)
    window = MainWindow()
    window.show()
    return app.exec()
