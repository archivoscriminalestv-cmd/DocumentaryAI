"""Production Readiness Checker del AIM.

Comprueba, por categoría, qué está listo para producción: herramientas locales (yt-dlp,
ffmpeg), recursos (knowledge/output/workspace/cache) y proveedores externos (credenciales +
integración). Determinista; ``root`` y ``prober`` inyectables. No descarga contenido.
"""

import importlib.util
import os
import shutil

from app.aim.models import Category, HealthState, ReadinessItem, ReadinessReport


def _tool_available(module: str | None = None, executable: str | None = None) -> bool:
    if module:
        try:
            if importlib.util.find_spec(module) is not None:
                return True
        except Exception:
            pass
    if executable and shutil.which(executable):
        return True
    return False


def _ffmpeg_available() -> bool:
    if shutil.which("ffmpeg"):
        return True
    try:
        import imageio_ffmpeg
        return bool(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        return False


def _resource_ready(path: str) -> bool:
    return os.path.isdir(path) or os.path.isdir(os.path.dirname(os.path.abspath(path)) or ".")


class ProductionReadinessChecker:
    def __init__(self, registry, *, root: str = ".") -> None:
        self._registry = registry
        self._root = root

    def check(self, *, probe: bool = False) -> ReadinessReport:
        items: list[ReadinessItem] = []

        # --- Learning (herramientas) -----------------------------------------
        items.append(self._tool("yt-dlp", Category.LEARNING,
                                 _tool_available(module="yt_dlp", executable="yt-dlp")))
        items.append(self._tool("ffmpeg", Category.LEARNING, _ffmpeg_available()))

        # --- Knowledge (recursos locales) ------------------------------------
        for name, rel in (("knowledge", "knowledge"), ("output", "output"),
                          ("workspace", os.path.join("output", "projects")),
                          ("cache", os.path.join("output", "cache"))):
            items.append(self._tool(name, Category.KNOWLEDGE,
                                    _resource_ready(os.path.join(self._root, rel))))

        # --- Proveedores externos (evidence + generation) --------------------
        for provider in self._registry.all():
            if provider.spec.category not in (Category.EVIDENCE, Category.GENERATION):
                continue
            items.append(self._provider(provider, probe=probe))

        ready = sum(1 for i in items if i.ready)
        pending = sum(1 for i in items if not i.ready and i.state != "missing")
        by_cat: dict[str, dict] = {}
        for i in items:
            agg = by_cat.setdefault(i.category, {"ready": 0, "total": 0})
            agg["total"] += 1
            agg["ready"] += 1 if i.ready else 0
        summary = {
            "ready": ready, "total": len(items), "pending": pending,
            "missing": sum(1 for i in items if i.state == "missing"),
            "production_ready": ready == len(items),
            "by_category": {k: by_cat[k] for k in sorted(by_cat)},
        }
        items.sort(key=lambda i: (i.category, i.name))
        return ReadinessReport(items=items, summary=summary)

    @staticmethod
    def _tool(name, category, available) -> ReadinessItem:
        return ReadinessItem(name=name, category=category, ready=bool(available),
                             state="ready" if available else "missing",
                             detail="disponible" if available else "no disponible")

    @staticmethod
    def _provider(provider, *, probe=False) -> ReadinessItem:
        h = provider.health(probe=probe)
        ready = h.state in HealthState.USABLE
        detail = {
            HealthState.READY: "listo (verificado)",
            HealthState.CONFIGURED: "listo (adaptador + credenciales)",
            HealthState.NOT_INTEGRATED: "adaptador pendiente",
            HealthState.NO_CREDENTIALS: f"falta credencial ({provider.spec.api_key_env})",
            HealthState.DISABLED: "deshabilitado",
            HealthState.AUTH_FAILED: "autenticación inválida",
            HealthState.RATE_LIMITED: "rate limit",
            HealthState.QUOTA: "cuota agotada",
            HealthState.SERVICE_DOWN: "servicio caído",
            HealthState.TIMEOUT: "timeout",
            HealthState.INVALID_RESPONSE: "respuesta inválida",
            HealthState.UNREACHABLE: "no responde",
        }.get(h.state, h.state)
        return ReadinessItem(name=provider.name, category=provider.spec.category, ready=ready,
                             state=h.state, detail=detail)
