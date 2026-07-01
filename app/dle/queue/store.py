"""Cola PERSISTENTE de aprendizaje. Si el proceso se cierra, al reabrir continúa.

Escritura atómica (tmp + replace): nunca se pierde trabajo. Dedup por URL: añadir la
misma URL dos veces no la duplica.
"""

import json
import os

from app.dle.queue import QUEUE_SCHEMA_VERSION
from app.dle.queue.models import QueueItem, QueueStatus


class QueueStore:
    def __init__(self, path: str = os.path.join("knowledge", "learning_queue.json")) -> None:
        self.path = path
        self._items: dict[str, QueueItem] = {}     # url -> item
        self._paused = False
        self._next_order = 0
        self.load()

    # ------------------------------------------------------------------ io
    def load(self) -> "QueueStore":
        self._items.clear()
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as h:
                    data = json.load(h)
                self._paused = bool(data.get("paused", False))
                self._next_order = int(data.get("next_order", 0))
                for raw in data.get("items", []):
                    item = QueueItem.from_dict(raw)
                    self._items[item.url] = item
            except (OSError, json.JSONDecodeError, TypeError):
                pass
        return self

    def save(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        payload = {
            "schema_version": QUEUE_SCHEMA_VERSION,
            "paused": self._paused,
            "next_order": self._next_order,
            "items": [i.to_dict() for i in self.ordered()],
        }
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as h:
            json.dump(payload, h, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    # ------------------------------------------------------------------ items
    def add(self, url: str) -> QueueItem:
        url = url.strip()
        if url in self._items:
            return self._items[url]               # dedup: no duplica
        item = QueueItem(url=url, order=self._next_order)
        self._next_order += 1
        self._items[url] = item
        return item

    def get(self, url: str) -> QueueItem | None:
        return self._items.get(url)

    def remove(self, url: str) -> bool:
        return self._items.pop(url, None) is not None

    def ordered(self) -> list[QueueItem]:
        return sorted(self._items.values(), key=lambda i: i.order)

    def by_status(self, status: str) -> list[QueueItem]:
        return [i for i in self.ordered() if i.status == status]

    # ------------------------------------------------------------------ control
    def is_paused(self) -> bool:
        return self._paused

    def set_paused(self, value: bool) -> None:
        self._paused = bool(value)

    def recover_inflight(self) -> int:
        """Devuelve los planos en vuelo (interrumpidos) a PENDING para re-procesarlos."""
        n = 0
        for item in self._items.values():
            if item.status in QueueStatus.IN_FLIGHT:
                item.status = QueueStatus.PENDING
                n += 1
        return n

    def clear_finished(self) -> int:
        done = [u for u, i in self._items.items() if i.status in QueueStatus.TERMINAL]
        for u in done:
            del self._items[u]
        return len(done)
