"""Memoria del documental: historial de todos los planos rodados.

El SDE recuerda cada plano para que cada decisión visual afecte a las siguientes
(LRU por dimensión). Determinista y serializable.
"""

from app.sde import SCHEMA_VERSION
from app.sde.models import VARIABLE_DIMENSIONS, ShotFingerprint, ShotRecord


class ShotHistory:
    def __init__(self) -> None:
        self._records: list[ShotRecord] = []

    def __len__(self) -> int:
        return len(self._records)

    def append(self, record: ShotRecord) -> None:
        self._records.append(record)

    def all(self) -> list[ShotRecord]:
        return list(self._records)

    def recent(self, n: int) -> list[ShotRecord]:
        return self._records[-n:] if n > 0 else []

    def recent_values(self, dim: str, n: int) -> list:
        return [getattr(r.fingerprint, dim) for r in self.recent(n)]

    def last_use_index(self, dim: str, value) -> int:
        """Índice global del último plano que usó ``value`` en ``dim`` (-1 si nunca)."""
        for r in reversed(self._records):
            if getattr(r.fingerprint, dim) == value:
                return r.index
        return -1

    def distribution(self, dim: str) -> dict:
        out: dict = {}
        for r in self._records:
            key = getattr(r.fingerprint, dim)
            out[key] = out.get(key, 0) + 1
        return out

    def to_dict(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "count": len(self._records),
            "shots": [r.to_dict() for r in self._records],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ShotHistory":
        hist = cls()
        for r in data.get("shots", []):
            fp = ShotFingerprint(**{k: v for k, v in r.get("fingerprint", {}).items()
                                    if k in ShotFingerprint.__dataclass_fields__})
            base = ShotFingerprint(**{k: v for k, v in r.get("base_fingerprint", {}).items()
                                      if k in ShotFingerprint.__dataclass_fields__})
            hist.append(ShotRecord(
                index=r.get("index", 0), shot_id=r.get("shot_id", ""), scene=r.get("scene", ""),
                narrative_mode=r.get("narrative_mode", ""), fingerprint=fp, base_fingerprint=base,
                diversity_score=r.get("diversity_score", 0.0), changes=list(r.get("changes", [])),
            ))
        return hist
