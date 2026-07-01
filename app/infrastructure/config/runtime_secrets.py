"""SecretsManager — inyección segura de secretos y configuración (Sprint C-11.5).

Capa de runtime: carga claves de API y modo de entorno SIN hardcodear nada.
No modifica el pipeline, el dominio ni los servicios; solo da acceso seguro a la
configuración.

- ``load_env()``     carga variables de entorno (incluyendo un ``.env`` opcional).
- ``get(key)``       devuelve el secreto o None (no falla si falta).
- ``require(key)``   devuelve el secreto o lanza RuntimeError si falta.
- ``is_production()``True si ENV=production; en otro caso, modo DEV.

Modos:
- DEV  → faltar claves está permitido (se activan fallbacks).
- PROD → faltar una clave requerida es fallo duro.
"""

import os

# Secretos soportados (no obligatorios salvo cuando se requieren explícitamente).
KNOWN_SECRETS = (
    "ELEVENLABS_API_KEY",
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
)


class SecretsManager:
    def __init__(self, env: dict[str, str] | None = None) -> None:
        # Por defecto usa el entorno real; inyectable para tests.
        self._env: dict[str, str] = env if env is not None else os.environ
        self._loaded = False

    def load_env(self, dotenv_path: str = ".env") -> bool:
        """Carga el entorno de forma segura. Lee un ``.env`` si existe.

        No sobreescribe variables ya presentes y nunca falla si el fichero no
        existe o no es legible. Devuelve True si la carga se completó.
        """
        try:
            if os.path.exists(dotenv_path):
                with open(dotenv_path, encoding="utf-8") as handle:
                    for raw in handle:
                        line = raw.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and key not in self._env:
                            self._env[key] = value
        except OSError:
            pass
        self._loaded = True
        return self._loaded

    @property
    def loaded(self) -> bool:
        return self._loaded

    def get(self, key: str) -> str | None:
        value = self._env.get(key)
        # Una cadena vacía se considera ausente.
        return value if value else None

    def require(self, key: str) -> str:
        value = self.get(key)
        if value is None:
            raise RuntimeError(
                f"Secreto requerido ausente: {key}. "
                "Defínelo en el entorno o en .env."
            )
        return value

    def is_production(self) -> bool:
        return str(self._env.get("ENV", "")).strip().lower() == "production"

    def runtime_mode(self) -> str:
        return "production" if self.is_production() else "dev"
