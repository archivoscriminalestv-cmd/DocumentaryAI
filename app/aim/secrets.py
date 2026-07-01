"""Secret Manager centralizado del AIM.

Busca credenciales en orden: variables de entorno → ``.env`` → configuración del proyecto.
NUNCA permite claves hardcodeadas, NUNCA las imprime y NUNCA las persiste. Solo informa de
si una credencial ESTÁ configurada (booleano) o devuelve una máscara; jamás el valor en logs.
Las fuentes son inyectables para tests deterministas.
"""

import os


def _parse_dotenv(path: str) -> dict:
    out: dict[str, str] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                out[key.strip()] = value.strip().strip('"').strip("'")
    except OSError:
        return {}
    return out


class SecretManager:
    def __init__(self, *, env: dict | None = None, dotenv_path: str | None = None,
                 config: dict | None = None) -> None:
        self._sources: list[dict] = []
        self._sources.append(dict(env) if env is not None else dict(os.environ))
        if dotenv_path and os.path.isfile(dotenv_path):
            self._sources.append(_parse_dotenv(dotenv_path))
        elif env is None and os.path.isfile(".env"):
            self._sources.append(_parse_dotenv(".env"))
        if config:
            self._sources.append(dict(config))

    def get(self, name: str) -> str | None:
        if not name:
            return None
        for source in self._sources:
            value = source.get(name)
            if value:
                return value
        return None

    def has(self, name: str) -> bool:
        return bool(self.get(name))

    @staticmethod
    def mask(name: str, value: str | None) -> str:
        return "configured" if value else "missing"     # nunca expone el valor
