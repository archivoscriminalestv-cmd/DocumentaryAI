"""IdentityConsistencyScore — mide si dos ``CharacterProfile`` describen a la MISMA
persona. 0.0 = totalmente distinta, 1.0 = la misma.

En CCE-001 NO se comparan imágenes: se comparan PERFILES (atributos visuales). La
comparación está detrás de una interfaz ``ProfileComparator`` para que en el futuro
un ``EmbeddingProfileComparator`` (embeddings faciales) sustituya al comparador por
atributos SIN tocar el resto del sistema.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from app.cce.models import MUTABLE_ATTRIBUTES, VISUAL_ATTRIBUTES, CharacterProfile


@dataclass
class IdentityConsistencyScore:
    score: float
    method: str = "attribute"
    comparable: int = 0
    matched: list[str] = field(default_factory=list)
    mismatched: list[str] = field(default_factory=list)
    only_in_a: list[str] = field(default_factory=list)
    only_in_b: list[str] = field(default_factory=list)
    same_identity_id: bool = False
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _norm(value: str) -> str:
    return " ".join(str(value or "").lower().split())


class ProfileComparator(Protocol):
    def compare(self, a: CharacterProfile, b: CharacterProfile) -> IdentityConsistencyScore:
        ...


class AttributeProfileComparator:
    """Compara atributos visuales INMUTABLES presentes en ambos perfiles.

    Los atributos mutables (ropa/accesorios) no penalizan la identidad. Si no hay
    atributos comparables, cae al id de identidad visual (mismo nombre canónico).
    """

    def compare(self, a: CharacterProfile, b: CharacterProfile) -> IdentityConsistencyScore:
        va, vb = a.attribute_values(), b.attribute_values()
        locked = [name for name, _ in VISUAL_ATTRIBUTES if name not in MUTABLE_ATTRIBUTES]

        matched, mismatched = [], []
        for name in locked:
            if name in va and name in vb:
                (matched if _norm(va[name]) == _norm(vb[name]) else mismatched).append(name)
        only_a = sorted(set(va) - set(vb))
        only_b = sorted(set(vb) - set(va))
        comparable = len(matched) + len(mismatched)
        same_vid = bool(a.visual_identity_id) and a.visual_identity_id == b.visual_identity_id

        if comparable == 0:
            # Sin solape de atributos: la identidad solo se sostiene por el id estable.
            score = 1.0 if same_vid else 0.0
        else:
            score = len(matched) / comparable

        return IdentityConsistencyScore(
            score=round(score, 4), method="attribute", comparable=comparable,
            matched=matched, mismatched=mismatched, only_in_a=only_a, only_in_b=only_b,
            same_identity_id=same_vid,
            details={"a": a.visual_identity_id, "b": b.visual_identity_id},
        )


class IdentityConsistencyScorer:
    """Fachada estable. Inyecta el comparador (por atributos hoy; embeddings mañana)."""

    def __init__(self, comparator: ProfileComparator | None = None) -> None:
        self._comparator = comparator or AttributeProfileComparator()

    def score(self, a: CharacterProfile, b: CharacterProfile) -> IdentityConsistencyScore:
        return self._comparator.compare(a, b)
