"""Persistencia del DKS: escribe los perfiles de estilo en ``knowledge/styles/``.

Reproducible (``sort_keys``, sin marcas de tiempo dentro de los perfiles). Cada perfil
va a su propio fichero ``<nombre>.json``.
"""

import json
import os


def write_styles(profiles: dict[str, dict], styles_dir: str) -> dict[str, str]:
    os.makedirs(styles_dir, exist_ok=True)
    paths: dict[str, str] = {}
    for name, profile in profiles.items():
        path = os.path.join(styles_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(profile, handle, ensure_ascii=False, indent=2, sort_keys=True)
        paths[name] = path
    return paths
