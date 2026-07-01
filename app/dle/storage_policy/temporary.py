"""TEMPORARY (por defecto): descargar → analizar → guardar conocimiento → BORRAR vídeo.

No deja residuos: al finalizar (con éxito o error) elimina todo el workspace temporal.
"""

from app.dle.storage_policy.base import TEMPORARY, BaseStoragePolicy, safe_rmtree


class TemporaryStoragePolicy(BaseStoragePolicy):
    mode = TEMPORARY

    def _finalize(self, work: str) -> None:
        safe_rmtree(work, allowed_root=self.temp_root)
