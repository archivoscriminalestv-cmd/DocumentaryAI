"""Modelos del Visual Provider Layer (VPL).

El VPL es la FRONTERA DE EJECUCIÓN entre la planificación cinematográfica y
cualquier tecnología de generación de imágenes. Consume ``VisualGenerationRequest``
(del VSC) y produce ``GeneratedAsset`` reales, normalizados e independientes del
proveedor. ``image_bytes`` es transitorio (no se serializa).
"""

from dataclasses import asdict, dataclass, field


@dataclass
class GeneratedAsset:
    shot_id: str
    scene_id: str
    provider: str
    model: str
    prompt: str
    negative_prompt: str
    seed: int
    width: int
    height: int
    generation_time: float = 0.0
    cost: float = 0.0
    filename: str = ""
    hash: str = ""
    reuse_key: str = ""
    cached: bool = False
    created_at: str = ""
    status: str = "generated"        # generated | cached | failed
    metadata: dict = field(default_factory=dict)
    image_bytes: bytes | None = None  # transitorio: NO se serializa

    @property
    def resolution(self) -> str:
        return f"{self.width}x{self.height}"

    def to_dict(self) -> dict:
        data = asdict(self)
        data.pop("image_bytes", None)
        # Alias con los nombres canónicos del manifest (sprint VPL-002).
        data["scene"] = self.scene_id
        data["resolution"] = self.resolution
        data["image_hash"] = self.hash
        data["cache"] = self.cached
        return data


@dataclass
class ProviderCapabilities:
    """Descripción declarativa de lo que un proveedor sabe hacer (VPL-003).

    Es un registro estático por adapter (independiente de credenciales). Permite
    a la orquestación/benchmark razonar sobre coste, negativos nativos, resolución
    máxima, formatos y modo de ejecución sin conocer internals del proveedor.
    """

    name: str
    model: str
    cost_per_image: float = 0.0
    native_negative_prompt: bool = False
    native_seed: bool = False
    max_width: int = 1024
    max_height: int = 1024
    aspect_ratios: list[str] = field(default_factory=list)
    async_polling: bool = False      # flujo submit -> poll (vs. respuesta directa)
    self_hostable: bool = False
    requires_api_key: str = ""       # nombre de la env var ("" = sin clave, p.ej. mock)
    available: bool = False          # runtime: credenciales presentes

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GenerationFailure:
    shot_id: str
    scene_id: str
    error: str
    retries: int = 0
    status: str = "failed"
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GenerationManifest:
    documentary_id: str
    provider: str
    model: str
    timestamp: str
    duration_seconds: float
    total: int
    cache_hits: int
    cache_misses: int
    failures: int
    retries: int
    assets: list[dict] = field(default_factory=list)
    failed: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
