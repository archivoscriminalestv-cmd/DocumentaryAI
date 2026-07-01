"""Arquitectura de VERIFICACIÓN del EAE (EAE-001) — solo contratos.

Define las piezas de verificación y cadena de custodia. NO calcula nada todavía: el
verificador base devuelve UNVERIFIED / UNKNOWN. La verificación real (comprobar la fuente,
hashes, duplicados, confianza) llegará en sprints posteriores.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.eae import UNKNOWN
from app.eae.models import ConfidenceLevel, Evidence, EvidenceVerification, VerificationStatus


@dataclass
class SourceVerification:
    """¿La evidencia procede de una fuente identificable y rastreable?"""
    has_source: str = UNKNOWN            # yes | no | UNKNOWN
    provider: str = ""
    url: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HashVerification:
    """¿Coincide el contenido con su hash registrado?"""
    sha256_matches: str = UNKNOWN
    perceptual_distance: float | None = None
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DuplicateDetection:
    is_duplicate: str = UNKNOWN
    duplicate_of: str = ""
    method: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ChainOfCustody:
    """Registro auditable de pasos: origen → adquisición → almacenamiento → uso."""
    steps: list[str] = field(default_factory=list)

    def add(self, step: str) -> None:
        self.steps.append(step)

    def to_dict(self) -> dict[str, Any]:
        return {"steps": list(self.steps)}


@dataclass
class EvidenceConfidence:
    level: str = ConfidenceLevel.UNKNOWN
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BaseEvidenceVerifier:
    """Implementa ``EvidenceVerifier`` como contrato: no calcula, devuelve UNVERIFIED."""

    name = "base"

    def verify(self, evidence: Evidence) -> EvidenceVerification:
        return EvidenceVerification(
            status=VerificationStatus.UNVERIFIED, confidence=ConfidenceLevel.UNKNOWN,
            source_verified=UNKNOWN, hash_verified=UNKNOWN,
            chain_of_custody=["acquired:contract-only"],
            notes=["EAE-001: verificación no implementada (solo arquitectura)"])
