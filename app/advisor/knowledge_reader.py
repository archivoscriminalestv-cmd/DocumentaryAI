"""Lector de artefactos PÚBLICOS de knowledge/ → CorpusSnapshot (solo lectura).

Tolerante a escrituras concurrentes: un fichero ausente o a medio escribir se trata
como no disponible (nunca lanza). No recorre ``documentaries/`` durante este sprint para
no interferir con un proceso de aprendizaje en curso: usa el agregado público
``learning_statistics.json`` + la presencia de ``styles/``.
"""

import json
import os

from app.advisor import UNKNOWN
from app.advisor.models import CAPABILITIES, CapabilityUsage, CorpusSnapshot

# Capacidades soportadas HOY por nuestro pipeline de generación (hecho conocido del
# sistema, no inferencia del corpus). El resto = UNKNOWN/no.
_PIPELINE_SUPPORT = {
    "real_footage": "no",       # generamos imágenes IA, no metraje real
    "interviews": "no",
    "maps": "no",
    "documents": "no",
    "archival_photos": "no",
    "reenactments": "no",
    "on_screen_text": "no",
    "b_roll": UNKNOWN,
    "narration": "yes",         # Composer sincroniza narración
    "music": "yes",             # Composer mezcla una cama musical
}


def _read_json(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as h:
            return json.load(h)
    except (OSError, json.JSONDecodeError, ValueError):
        return None  # a medio escribir / corrupto -> no disponible


class KnowledgeReader:
    """Implementación por defecto de ``KnowledgeSource`` (solo lectura)."""

    def __init__(self, knowledge_root: str = "knowledge") -> None:
        self.root = knowledge_root

    def snapshot(self) -> CorpusSnapshot:
        snap = CorpusSnapshot()
        stats = _read_json(os.path.join(self.root, "learning_statistics.json"))
        if stats is not None:
            snap.available = True
            snap.sources_read.append("learning_statistics.json")
            snap.documentaries = int(stats.get("documentaries_learned", 0) or 0)
            snap.hours = float(stats.get("hours_learned", 0.0) or 0.0)
            snap.shots = int(stats.get("shots_analyzed", 0) or 0)
            snap.scenes = int(stats.get("scenes", 0) or 0)

        styles_dir = os.path.join(self.root, "styles")
        if os.path.isdir(styles_dir):
            try:
                for name in sorted(os.listdir(styles_dir)):
                    if name.endswith(".json"):
                        snap.sources_read.append(os.path.join("styles", name))
                snap.available = True
            except OSError:
                pass
            self._load_styles(styles_dir, snap)

        snap.capabilities = [
            CapabilityUsage(capability=c, corpus_percent=None,
                            pipeline_supported=_PIPELINE_SUPPORT.get(c, UNKNOWN),
                            note="cobertura del corpus pendiente de señal pública")
            for c in CAPABILITIES
        ]
        return snap

    # --- carga de distribuciones medidas (DKS) -------------------------------

    def _load_styles(self, styles_dir: str, snap: CorpusSnapshot) -> None:
        """Vuelca las distribuciones/estadísticas medidas de DKS al snapshot.

        Tolerante al esquema: solo recoge dicts con forma {counts,fractions,total}
        (distribución) o {count,mean,median,...} (numérica). Defensivo."""
        files = {
            "motion_patterns.json": ("movement",),
            "lighting_patterns.json": ("lighting", "color_temperature", "dominant_color"),
            "cinematography_patterns.json": ("shot_size", "composition", "close_up_frequency"),
            "editing_patterns.json": ("pacing_tier", "cuts_per_minute", "shot_length"),
        }
        for fname, keys in files.items():
            data = _read_json(os.path.join(styles_dir, fname))
            if not isinstance(data, dict):
                continue
            for key in keys:
                value = data.get(key)
                if not isinstance(value, dict):
                    continue
                if "counts" in value and "fractions" in value:
                    snap.dimensions[key] = {
                        "counts": dict(value.get("counts", {})),
                        "fractions": dict(value.get("fractions", {})),
                        "total": int(value.get("total", 0) or 0),
                    }
                elif "mean" in value or "median" in value:
                    snap.numeric[key] = {k: value.get(k) for k in
                                         ("count", "mean", "median", "min", "max", "stdev")}
            total = data.get("total_shots")
            if isinstance(total, int) and total > snap.measured_shots:
                snap.measured_shots = total
            docs = data.get("documentaries")
            if isinstance(docs, int) and docs > snap.documentaries_measured:
                snap.documentaries_measured = docs
