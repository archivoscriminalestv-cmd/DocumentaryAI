"""Gap Analyzer (DCA-003) — convierte diferencias medidas en huecos objetivos con dueño.

Cada hueco es un HECHO (nunca una opinión) y se mapea al subsistema responsable. Determinista.
"""

from app.dca.evaluation.models import Gap, MetricStatus

# Dimensión -> subsistema responsable (capability mapping).
_OWNER = {
    "pacing": "VIS", "average_shot_duration": "VIS",
    "movement": "VAI", "color_temperature": "VAI",
    "lighting": "VUE",
    "evidence_coverage": "EAE", "evidence_utilization": "Composer",
    "chronology": "ECE", "recreation_usage": "Composer",
    "narration": "Narration", "music": "Music",
}


def _describe(metric) -> str:
    if metric.kind == "numeric" and metric.deviation is not None:
        return f"{metric.dimension} difiere {round(metric.deviation * 100)}% " \
               f"(corpus {metric.corpus_value}{metric.unit}, generado {metric.generated_value}{metric.unit})"
    if metric.kind == "coverage" and metric.deviation is not None:
        return f"{metric.dimension}: {metric.generated_value}/{metric.corpus_value} " \
               f"({round((1 - metric.deviation) * 100)}% cubierto)"
    return f"{metric.dimension} difiere (corpus {metric.corpus_value}, generado {metric.generated_value})"


def analyze_gaps(comparisons) -> list[Gap]:
    gaps: list[Gap] = []
    for metric in comparisons:
        if metric.status != MetricStatus.DIFFERS:
            continue
        gaps.append(Gap(
            id=f"gap:{metric.dimension}", dimension=metric.dimension,
            description=_describe(metric),
            magnitude=metric.deviation if metric.deviation is not None else 1.0,
            owner=_OWNER.get(metric.dimension, "UNKNOWN"), kind="generation"))
    gaps.sort(key=lambda g: g.id)
    return gaps


def owner_of(dimension: str) -> str:
    return _OWNER.get(dimension, "UNKNOWN")
