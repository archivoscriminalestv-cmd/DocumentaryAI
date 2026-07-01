"""LogTail (DAS-001A) — lee incrementalmente el log del proceso de aprendizaje.

El proceso learn_queue redirige su salida a un fichero de log (no a pipes de la UI, para poder
sobrevivir al cierre de Studio). LogTail lee ese fichero de forma incremental y devuelve solo
las líneas NUEVAS desde la última lectura, para volcarlas al Log de Studio. Sin Qt, testeable.

Maneja rotación/truncado (si el fichero encoge, reinicia el offset) y ausencia del fichero.
"""

import os


class LogTail:
    def __init__(self, path: str) -> None:
        self._path = path
        self._offset = 0

    def reset(self) -> None:
        """Vuelve a leer desde el principio."""
        self._offset = 0

    def attach_end(self) -> None:
        """Salta al final actual: solo se leerán las líneas que lleguen a partir de ahora.

        Se usa al reconectar con un aprendizaje ya en curso para no volcar todo el histórico."""
        try:
            self._offset = os.path.getsize(self._path)
        except OSError:
            self._offset = 0

    def read_new(self) -> list[str]:
        """Devuelve las líneas nuevas (no vacías) añadidas desde la última llamada."""
        if not os.path.exists(self._path):
            return []
        try:
            size = os.path.getsize(self._path)
            if size < self._offset:          # el fichero se truncó/rotó → releer desde el inicio
                self._offset = 0
            with open(self._path, "r", encoding="utf-8", errors="replace") as fh:
                fh.seek(self._offset)
                data = fh.read()
                self._offset = fh.tell()
        except OSError:
            return []
        return [line for line in data.splitlines() if line.strip()]
