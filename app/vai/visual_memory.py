"""VisualMemory — almacén de las decisiones de VAI (sin IA).

Todavía NO aprende ni infiere: solo guarda qué especificación tomó VAI por plano,
para poder reutilizarla o auditarla más adelante (coherencia estética, depuración,
y base para una futura capa de memoria/IA). Opcionalmente persiste a JSON.
"""

import json
import os
from dataclasses import asdict

from app.vai.models import VisualSpecification


class VisualMemory:
    def __init__(self, persist_path: str | None = None) -> None:
        self._by_shot: dict[str, VisualSpecification] = {}
        self._order: list[str] = []
        self._persist_path = persist_path

    def record(self, shot_id: str, spec: VisualSpecification) -> None:
        if shot_id not in self._by_shot:
            self._order.append(shot_id)
        self._by_shot[shot_id] = spec
        if self._persist_path:
            self._save()

    def get(self, shot_id: str) -> VisualSpecification | None:
        return self._by_shot.get(shot_id)

    def all(self) -> list[VisualSpecification]:
        return [self._by_shot[s] for s in self._order]

    def _save(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self._persist_path)), exist_ok=True)
        data = [asdict(self._by_shot[s]) for s in self._order]
        with open(self._persist_path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
