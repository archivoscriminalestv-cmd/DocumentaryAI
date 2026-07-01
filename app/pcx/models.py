"""Modelos del Production Context (PCX).

``ProductionContext`` representa todo lo que un documental necesita conocer ANTES de
generarse. Hoy solo contiene las decisiones de generación (del KBG, ya filtradas: nunca
``UNKNOWN``) expuestas de forma NEUTRAL (los consumidores no ven tipos del KBG). Está
diseñado para admitir, sin romper contratos, cobertura de evidencias, política de
recreación, restricciones, plataforma, duración, audiencia, idioma, metadatos del caso y
preferencias. Tipado, determinista, serializable.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.pcx import SCHEMA_VERSION, UNKNOWN


@dataclass
class DecisionView:
    """Vista neutral de una decisión de generación (sin acoplar al KBG)."""
    value: Any
    confidence: float = 0.0
    origin: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProductionContext:
    schema_version: str = SCHEMA_VERSION
    genre: str = UNKNOWN
    # Solo decisiones CONOCIDAS: sección -> clave -> DecisionView. UNKNOWN ya filtrado.
    generation: dict[str, dict[str, DecisionView]] = field(default_factory=dict)
    # --- reservado para futuros sprints (contrato preparado, no implementado) ---
    evidence_coverage: Any = None
    recreation_policy: Any = None
    project_constraints: dict = field(default_factory=dict)
    target_platform: str = UNKNOWN
    duration: float | None = None
    audience: str = UNKNOWN
    language: str = UNKNOWN
    case_metadata: dict = field(default_factory=dict)
    production_preferences: dict = field(default_factory=dict)
    user_preferences: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ API pública
    def decision(self, section: str, key: str) -> DecisionView | None:
        return self.generation.get(section, {}).get(key)

    def has(self, section: str, key: str, *, min_confidence: float = 0.0) -> bool:
        d = self.decision(section, key)
        return d is not None and d.value != UNKNOWN and d.confidence >= min_confidence

    def get(self, section: str, key: str, *, min_confidence: float = 0.0, default=None):
        """Devuelve el valor SOLO si la decisión existe, es conocida y tiene confianza
        suficiente; en cualquier otro caso, ``default`` (la generación sigue igual)."""
        d = self.decision(section, key)
        if d is None or d.value == UNKNOWN or d.confidence < min_confidence:
            return default
        return d.value

    @property
    def is_empty(self) -> bool:
        return not any(self.generation.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "genre": self.genre,
            "generation": {sec: {k: v.to_dict() for k, v in decs.items()}
                           for sec, decs in self.generation.items()},
            "target_platform": self.target_platform,
            "duration": self.duration,
            "audience": self.audience,
            "language": self.language,
            "case_metadata": self.case_metadata,
            "production_preferences": self.production_preferences,
            "user_preferences": self.user_preferences,
        }
