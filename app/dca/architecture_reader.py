"""Lector de información PÚBLICA de la arquitectura (DCA).

Lee únicamente artefactos públicos del repositorio: ADR, RFC, SPEC, READMEs de los
subsistemas y esquemas. NUNCA introspecciona código privado ni importa motores. Solo
lista ficheros (determinista, ordenado). La raíz es inyectable para los tests.
"""

import os


class ArchitectureReader:
    def __init__(self, root: str = ".") -> None:
        self.root = root

    def _list_md(self, *parts) -> list[str]:
        path = os.path.join(self.root, *parts)
        if not os.path.isdir(path):
            return []
        return sorted(f for f in os.listdir(path) if f.endswith((".md", ".json")))

    def docs_index(self) -> dict:
        adrs = self._list_md("docs", "adr")
        rfcs = self._list_md("docs", "rfc")
        specs = self._list_md("docs", "spec")
        app_dir = os.path.join(self.root, "app")
        readmes = []
        if os.path.isdir(app_dir):
            for name in sorted(os.listdir(app_dir)):
                if os.path.isfile(os.path.join(app_dir, name, "README.md")):
                    readmes.append(name)
        return {
            "adr": adrs, "rfc": rfcs, "spec": specs,
            "subsystem_readmes": readmes,
            "counts": {"adr": len(adrs), "rfc": len(rfcs), "spec": len(specs),
                       "readmes": len(readmes)},
        }
