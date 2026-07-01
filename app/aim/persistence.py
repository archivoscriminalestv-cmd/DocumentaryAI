"""Persistencia del AIM — escribe SOLO en ``output/system/``. NUNCA credenciales/prompts."""

import json
import os


def _dump(path: str, payload) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def write_outputs(out_dir: str, manager, *, probe: bool = False) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    paths = {name: os.path.join(out_dir, name) for name in (
        "production_readiness.json", "provider_status.json", "provider_capabilities.json",
        "provider_metrics.json")}

    _dump(paths["production_readiness.json"], manager.readiness(probe=probe).to_dict())
    _dump(paths["provider_status.json"], {"providers": manager.provider_status(probe=probe)})
    _dump(paths["provider_capabilities.json"], manager.capability_matrix())
    _dump(paths["provider_metrics.json"],
          {"metrics": manager.metrics(), "summary": manager.metrics_summary()})
    return paths
