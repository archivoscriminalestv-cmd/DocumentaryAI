"""Experiment layer — versionado reproducible y comparación A/B (Sprint C-11).

Convierte DocumentaryAI en "un sistema de media reproducible con evolución
medible": cada render se etiqueta con ``pipeline_version`` y métricas (ratios de
caché, tiempo, coste), y se pueden comparar varias versiones sobre el mismo input.

Es ADITIVO: no modifica el dominio ni ``FinalRenderService`` (C-10). Lee el
``FinalRender`` y enriquece su informe. La identidad de voz es global e inmutable
(``CHANNEL_IDENTITY``).
"""

import json
import os

from app.application.channel_identity import CHANNEL_IDENTITY

PIPELINE_VERSION = "C-11"


def _ratio(hits: int, misses: int) -> float:
    total = hits + misses
    return round(hits / total, 4) if total else 0.0


def _metrics(report: dict) -> dict:
    return {
        "voice_cache_hit_ratio": _ratio(
            int(report.get("voice_cache_hits", 0)),
            int(report.get("voice_cache_misses", 0)),
        ),
        "image_cache_hit_ratio": _ratio(
            int(report.get("image_cache_hits", 0)),
            int(report.get("image_cache_misses", 0)),
        ),
        "render_time_ms": int(report.get("render_time_ms", 0)),
    }


def extended_report(
    final_render,
    *,
    pipeline_version: str = PIPELINE_VERSION,
    comparison_mode: bool = False,
    scene_count: int | None = None,
) -> dict:
    """FinalRender JSON extendido con identidad de canal, versión y métricas."""
    report = dict(final_render.report)  # copia; no muta el dominio
    count = scene_count if scene_count is not None else len(final_render.scenes_audio)
    report.update(
        {
            "pipeline_version": pipeline_version,
            "voice_profile": CHANNEL_IDENTITY.voice_profile(),
            "metrics": _metrics(report),
            "scene_count": count,
            "comparison_mode": comparison_mode,
        }
    )
    return report


def compact_output(report: dict, *, comparison_available: bool) -> dict:
    """Salida compacta del contrato C-11."""
    return {
        "final_video_path": report.get("final_video_path", ""),
        "pipeline_version": report.get("pipeline_version", PIPELINE_VERSION),
        "metrics": report.get("metrics", {}),
        "comparison_available": comparison_available,
    }


class ExperimentRunner:
    """Ejecuta el render etiquetando versión y métricas; soporta comparación A/B."""

    def __init__(self, render_service, *, pipeline_version: str = PIPELINE_VERSION) -> None:
        self._render = render_service
        self._version = pipeline_version
        self._enforce_voice_identity()

    def _enforce_voice_identity(self) -> None:
        # La voz es GLOBAL e INMUTABLE: el render debe usar el voice_id de canal.
        configured = getattr(self._render, "_voice_id", None)
        if configured is not None and configured != CHANNEL_IDENTITY.voice_id:
            raise ValueError(
                f"voice_id no permitido: {configured!r}. "
                f"La identidad de canal exige {CHANNEL_IDENTITY.voice_id!r}."
            )

    def run(self, scenes: list, *, comparison_mode: bool = False) -> dict:
        final = self._render.render(scenes)
        return extended_report(
            final, pipeline_version=self._version, comparison_mode=comparison_mode
        )

    def compare(self, variants: dict[str, list], *, out_path: str | None = None) -> dict:
        """same_input → múltiples versiones. Devuelve (y opcionalmente escribe) el comparison_report."""
        results: dict[str, dict] = {}
        for version, scenes in variants.items():
            final = self._render.render(scenes)
            results[version] = extended_report(
                final, pipeline_version=version, comparison_mode=True
            )

        comparison = {
            "comparison_mode": True,
            "versions": list(variants.keys()),
            "voice_profile": CHANNEL_IDENTITY.voice_profile(),
            "results": results,
        }
        if out_path:
            parent = os.path.dirname(os.path.abspath(out_path))
            os.makedirs(parent, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as handle:
                json.dump(comparison, handle, ensure_ascii=False, indent=2)
        return comparison
