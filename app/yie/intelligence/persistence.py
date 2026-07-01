"""Persistencia de inteligencia competitiva (YIE-002).

Escribe ficheros NUEVOS por documental (no toca los del YIE-001 ni los del DLE):
    channel.json · audience.json · engagement.json · competitive.json · provider_coverage.json
Reproducible (``sort_keys``).
"""

import json
import os


def _dump(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def write_competitive(doc_dir: str, channel, audience, engagement,
                      competitive: dict, coverage) -> dict[str, str]:
    os.makedirs(doc_dir, exist_ok=True)
    paths = {
        "channel": os.path.join(doc_dir, "channel.json"),
        "audience": os.path.join(doc_dir, "audience.json"),
        "engagement": os.path.join(doc_dir, "engagement.json"),
        "competitive": os.path.join(doc_dir, "competitive.json"),
        "provider_coverage": os.path.join(doc_dir, "provider_coverage.json"),
    }
    _dump(paths["channel"], channel.to_dict())
    _dump(paths["audience"], audience.to_dict())
    _dump(paths["engagement"], engagement.to_dict())
    _dump(paths["competitive"], competitive)
    _dump(paths["provider_coverage"], coverage.to_dict())
    return paths
