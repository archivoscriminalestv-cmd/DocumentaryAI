"""Modelos del API Integration Manager (AIM).

Tipados, deterministas, serializables. ``ProviderSpec`` es el contrato público y declarativo
de un proveedor externo; ``HealthStatus`` el resultado de su comprobación; ``ReadinessReport``
el informe de preparación para producción. Nunca contiene credenciales.
"""

from dataclasses import asdict, dataclass, field
from typing import Any


class Category:
    LEARNING = "learning"
    EVIDENCE = "evidence"
    GENERATION = "generation"
    KNOWLEDGE = "knowledge"
    ALL = (LEARNING, EVIDENCE, GENERATION, KNOWLEDGE)


class Capability:
    LLM = "llm"
    EMBEDDINGS = "embeddings"
    IMAGE = "image"
    VIDEO = "video"
    VOICE = "voice"
    MUSIC = "music"
    OCR = "ocr"
    TRANSLATION = "translation"
    EVIDENCE = "evidence"
    MAPS = "maps"
    TIMELINE = "timeline"
    DISCOVERY = "discovery"
    TRANSCRIPTION = "transcription"
    DOWNLOAD = "download"


class ProviderStatus:
    AVAILABLE = "available"     # adaptador real integrado y usable
    CONTRACT = "contract"       # declarado; integración pendiente
    DISABLED = "disabled"       # no usar
    ALL = (AVAILABLE, CONTRACT, DISABLED)


class HealthState:
    READY = "ready"                 # adaptador + credenciales + probe real OK
    CONFIGURED = "configured"       # adaptador + credenciales OK, sin probe real
    NO_CREDENTIALS = "no_credentials"
    NOT_INTEGRATED = "not_integrated"   # sin adaptador real todavía (contrato)
    DISABLED = "disabled"
    UNREACHABLE = "unreachable"
    # estados de error clasificados (probe real)
    AUTH_FAILED = "auth_failed"
    RATE_LIMITED = "rate_limited"
    QUOTA = "quota_exceeded"
    SERVICE_DOWN = "service_down"
    INVALID_RESPONSE = "invalid_response"
    TIMEOUT = "timeout"
    # estados que cuentan como "usable" en producción
    USABLE = (READY, CONFIGURED)


@dataclass
class ProviderSpec:
    name: str
    category: str
    capabilities: list[str] = field(default_factory=list)
    status: str = ProviderStatus.CONTRACT
    version: str = "1"
    documentation: str = ""
    requires_api_key: bool = False
    api_key_env: str = ""                 # nombre de la variable; NUNCA el valor
    known_limits: dict = field(default_factory=dict)
    cost: str = "UNKNOWN"                  # free | paid | restricted | UNKNOWN
    timeout: float = 30.0
    retries: int = 2
    priority: int = 100                   # menor = preferente
    alternative: str = ""                 # proveedor alternativo (fallback explícito)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HealthStatus:
    provider: str
    state: str = HealthState.NOT_INTEGRATED
    available: bool = False               # adaptador integrado
    authenticated: str = "UNKNOWN"        # yes | no | not_required
    reachable: str = "UNKNOWN"            # yes | no | UNKNOWN (sin red por defecto)
    latency_ms: float | None = None
    quota: str = "UNKNOWN"
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionResult:
    provider: str = ""
    operation: str = ""
    status: str = "error"                 # ok | error | unavailable | skipped
    value: Any = "UNKNOWN"                 # UNKNOWN antes que inventar
    error_class: str = "NONE"             # AUTH | TIMEOUT | QUOTA | RATE_LIMIT | ...
    retries: int = 0
    latency_ms: float | None = None
    note: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "ok"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProviderMetric:
    """Métrica OBJETIVA de una operación. Nunca prompts, datos ni credenciales."""
    provider: str
    operation: str
    success: bool
    duration_ms: float
    retries: int = 0
    error_class: str = "NONE"
    cost: str = "UNKNOWN"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReadinessItem:
    name: str
    category: str
    ready: bool = False
    state: str = ""
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReadinessReport:
    schema_version: str = "0.1"
    items: list[ReadinessItem] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version,
                "items": [i.to_dict() for i in self.items], "summary": self.summary}
