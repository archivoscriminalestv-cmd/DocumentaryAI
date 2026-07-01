"""Preflight de credenciales del VPL.

Antes de generar ninguna imagen, comprueba qué proveedores tienen credenciales y si
esas credenciales son VÁLIDAS mediante una llamada real y barata (listar modelos),
sin coste de generación. Reporta el estado de cada proveedor de forma clara.

HTTP inyectable (``http_get``) para tests sin red. No lanza: clasifica cada
proveedor y deja que el pipeline siga con la estrategia de fallback.
"""

import os
from dataclasses import dataclass

from app.vpl.http import get_json
from app.vpl.provider import ProviderError

# Estados posibles del preflight.
OK = "OK"
INVALID = "Clave inválida"
NOT_CONFIGURED = "No configurado"
ERROR = "Error"

# Etiquetas legibles + endpoints de validación (listado de modelos/cuenta = sin coste).
_PROVIDERS = [
    ("openai", "OpenAI", "OPENAI_API_KEY"),
    ("imagen", "Google Imagen", "GOOGLE_API_KEY"),
    ("huggingface", "Hugging Face", "HF_TOKEN"),
    ("replicate", "Replicate", "REPLICATE_API_TOKEN"),
]


@dataclass
class PreflightResult:
    name: str
    label: str
    status: str
    valid: bool
    detail: str = ""

    def to_dict(self) -> dict:
        return {"provider": self.name, "label": self.label, "status": self.status,
                "valid": self.valid, "detail": self.detail}


def _validate_openai(api_key: str, http_get, timeout: float) -> tuple[str, str]:
    http_get("https://api.openai.com/v1/models", {"Authorization": f"Bearer {api_key}"}, timeout)
    return OK, ""


def _validate_imagen(api_key: str, http_get, timeout: float) -> tuple[str, str]:
    http_get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}", {}, timeout)
    return OK, ""


def _validate_flux(api_key: str, http_get, timeout: float) -> tuple[str, str]:
    # BFL no expone un "list models" estándar; validamos a nivel de credencial con un
    # GET autenticado. Cualquier 2xx/!=auth se considera credencial aceptada.
    http_get("https://api.bfl.ml/v1/get_result?id=preflight",
             {"x-key": api_key, "accept": "application/json"}, timeout)
    return OK, ""


def _validate_huggingface(token: str, http_get, timeout: float) -> tuple[str, str]:
    info = http_get("https://huggingface.co/api/whoami-v2", {"Authorization": f"Bearer {token}"}, timeout)
    name = info.get("name") if isinstance(info, dict) else ""
    return OK, (f"user={name}" if name else "")


def _validate_replicate(token: str, http_get, timeout: float) -> tuple[str, str]:
    info = http_get("https://api.replicate.com/v1/account", {"Authorization": f"Bearer {token}"}, timeout)
    name = info.get("username") if isinstance(info, dict) else ""
    return OK, (f"account={name}" if name else "")


_VALIDATORS = {
    "openai": _validate_openai,
    "imagen": _validate_imagen,
    "flux": _validate_flux,
    "huggingface": _validate_huggingface,
    "replicate": _validate_replicate,
}


def check_provider(name: str, label: str, env_var: str, *, http_get=get_json,
                   timeout: float = 20.0) -> PreflightResult:
    api_key = os.environ.get(env_var, "").strip()
    if not api_key:
        return PreflightResult(name, label, NOT_CONFIGURED, valid=False)
    try:
        status, detail = _VALIDATORS[name](api_key, http_get, timeout)
        return PreflightResult(name, label, status, valid=True, detail=detail)
    except ProviderError as exc:
        # 4xx (incl. auth) => clave inválida; transitorio (red/5xx) => error recuperable.
        if exc.transient:
            return PreflightResult(name, label, ERROR, valid=False, detail=str(exc))
        return PreflightResult(name, label, INVALID, valid=False, detail=str(exc))
    except Exception as exc:  # noqa: BLE001
        return PreflightResult(name, label, ERROR, valid=False, detail=str(exc))


def run_preflight(*, http_get=get_json, timeout: float = 20.0) -> list[PreflightResult]:
    return [check_provider(n, label, env, http_get=http_get, timeout=timeout)
            for n, label, env in _PROVIDERS]


def format_report(results: list[PreflightResult], width: int = 20) -> str:
    """Informe alineado con puntos:  ``OpenAI ............. OK``.

    Si un proveedor da error, se muestra el motivo EXACTO (no se ocultan errores).
    """
    lines = []
    for r in results:
        dots = "." * max(1, width - len(r.label) - 1)
        line = f"{r.label} {dots} {r.status}"
        if r.detail:
            line += f"  ({r.detail[:120]})"
        lines.append(line)
    return "\n".join(lines)


def valid_providers(results: list[PreflightResult]) -> list[str]:
    """Nombres de proveedores con credencial válida, en orden de preflight."""
    return [r.name for r in results if r.valid]


def format_full(results: list[PreflightResult], available_ordered: list[str]) -> str:
    """Bloque completo del preflight (cabecera + estados + proveedores disponibles)."""
    by_name = {r.name: r for r in results}
    lines = ["Checking providers...", "", format_report(results), "", "Available providers:", ""]
    if available_ordered:
        for i, name in enumerate(available_ordered, start=1):
            label = by_name[name].label if name in by_name else name
            lines.append(f"  {i}. {label}")
    else:
        lines.append("  (ninguno)")
    return "\n".join(lines)
