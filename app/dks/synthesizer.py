"""KnowledgeSynthesizer — agrega el corpus del DLE en perfiles de estilo (DKS).

Produce seis perfiles (true_crime, documentary_style, cinematography_patterns,
editing_patterns, motion_patterns, lighting_patterns). Solo agrega (medias, medianas,
histogramas, distribuciones, correlaciones). NUNCA infiere ni etiqueta semánticamente.
Determinista y reproducible.
"""

from app.dks import DKS_VERSION, SCHEMA_VERSION
from app.dks.loader import Corpus
from app.dks.stats import distribution, histogram, pearson, summarize


def _doc_stat(corpus: Corpus, key: str) -> list[float]:
    out = []
    for doc in corpus.documentaries:
        if key in doc.statistics:
            try:
                out.append(float(doc.statistics[key]))
            except (TypeError, ValueError):
                pass
    return out


def _shot_numeric(shots: list[dict], key: str) -> list[float]:
    out = []
    for shot in shots:
        value = shot.get(key)
        if isinstance(value, (int, float)):
            out.append(float(value))
    return out


def _shot_categorical(shots: list[dict], key: str) -> dict:
    counts: dict[str, int] = {}
    for shot in shots:
        label = str(shot.get(key, "UNKNOWN"))
        counts[label] = counts.get(label, 0) + 1
    return counts


def _scalar_distribution(corpus: Corpus, key: str) -> dict:
    counts: dict[str, int] = {}
    for doc in corpus.documentaries:
        label = str(doc.statistics.get(key, "UNKNOWN"))
        counts[label] = counts.get(label, 0) + 1
    return distribution([counts])


def _paired(shots: list[dict], a: str, b: str):
    xs, ys = [], []
    for shot in shots:
        va, vb = shot.get(a), shot.get(b)
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            xs.append(float(va))
            ys.append(float(vb))
    return xs, ys


class KnowledgeSynthesizer:
    def __init__(self, corpus: Corpus) -> None:
        self.corpus = corpus
        self.shots = corpus.all_shots()

    def _header(self, name: str, extra: dict | None = None) -> dict:
        head = {
            "schema_version": SCHEMA_VERSION,
            "dks_version": DKS_VERSION,
            "name": name,
            "documentaries": len(self.corpus),
            "total_shots": len(self.shots),
        }
        if extra:
            head.update(extra)
        return head

    # ------------------------------------------------------------------ perfiles
    def cinematography(self) -> dict:
        profile = self._header("cinematography_patterns")
        profile["shot_size"] = distribution([_shot_categorical(self.shots, "shot_size")])
        profile["composition"] = distribution([_shot_categorical(self.shots, "composition")])
        profile["close_up_frequency"] = summarize(_doc_stat(self.corpus, "close_up_frequency"))
        return profile

    def editing(self) -> dict:
        durations = _shot_numeric(self.shots, "duration")
        profile = self._header("editing_patterns")
        profile["shot_length"] = summarize(durations)
        profile["shot_length_histogram"] = histogram(durations)
        profile["cuts_per_minute"] = summarize(_doc_stat(self.corpus, "cuts_per_minute"))
        profile["average_shot_length_per_doc"] = summarize(
            _doc_stat(self.corpus, "average_shot_length"))
        profile["pacing_tier"] = _scalar_distribution(self.corpus, "pacing_tier")
        cx, cy = _doc_stat(self.corpus, "average_shot_length"), _doc_stat(self.corpus, "cuts_per_minute")
        profile["correlations"] = {"avg_shot_length__cuts_per_minute": pearson(cx, cy)}
        return profile

    def motion(self) -> dict:
        magnitudes = _shot_numeric(self.shots, "motion_magnitude")
        profile = self._header("motion_patterns")
        profile["movement"] = distribution([_shot_categorical(self.shots, "movement")])
        profile["motion_magnitude"] = summarize(magnitudes)
        profile["motion_magnitude_histogram"] = histogram(magnitudes)
        dur, mot = _paired(self.shots, "duration", "motion_magnitude")
        profile["correlations"] = {"duration__motion_magnitude": pearson(dur, mot)}
        return profile

    def lighting(self) -> dict:
        brightness = _shot_numeric(self.shots, "brightness")
        contrast = _shot_numeric(self.shots, "contrast")
        profile = self._header("lighting_patterns")
        profile["lighting"] = distribution([_shot_categorical(self.shots, "lighting")])
        profile["color_temperature"] = distribution(
            [_shot_categorical(self.shots, "color_temperature")])
        profile["dominant_color"] = distribution([_shot_categorical(self.shots, "dominant_color")])
        profile["brightness"] = summarize(brightness)
        profile["brightness_histogram"] = histogram(brightness)
        profile["contrast"] = summarize(contrast)
        bx, cy = _paired(self.shots, "brightness", "contrast")
        profile["correlations"] = {"brightness__contrast": pearson(bx, cy)}
        return profile

    def documentary_style(self, name: str = "documentary_style", extra: dict | None = None) -> dict:
        profile = self._header(name, extra)
        profile["corpus"] = {
            "documentaries": len(self.corpus),
            "total_shots": sum(int(d.statistics.get("shot_count", 0)) for d in self.corpus.documentaries),
            "total_scenes": sum(int(d.statistics.get("scene_count", 0)) for d in self.corpus.documentaries),
            "total_duration_seconds": round(sum(d.duration for d in self.corpus.documentaries), 3),
            "hours": round(sum(d.duration for d in self.corpus.documentaries) / 3600.0, 4),
        }
        profile["per_documentary"] = {
            "shot_count": summarize(_doc_stat(self.corpus, "shot_count")),
            "scene_count": summarize(_doc_stat(self.corpus, "scene_count")),
            "average_shot_length": summarize(_doc_stat(self.corpus, "average_shot_length")),
            "cuts_per_minute": summarize(_doc_stat(self.corpus, "cuts_per_minute")),
            "close_up_frequency": summarize(_doc_stat(self.corpus, "close_up_frequency")),
        }
        profile["pacing_tier"] = _scalar_distribution(self.corpus, "pacing_tier")
        profile["distributions"] = {
            "shot_size": distribution([_shot_categorical(self.shots, "shot_size")]),
            "movement": distribution([_shot_categorical(self.shots, "movement")]),
            "lighting": distribution([_shot_categorical(self.shots, "lighting")]),
            "color_temperature": distribution([_shot_categorical(self.shots, "color_temperature")]),
        }
        return profile

    def synthesize(self) -> dict[str, dict]:
        """Devuelve {nombre_de_fichero: perfil}. Las claves son los ficheros de salida."""
        cinematography = self.cinematography()
        editing = self.editing()
        motion = self.motion()
        lighting = self.lighting()
        overall = self.documentary_style()
        # true_crime: MISMA síntesis agregada del corpus, etiquetada. No se infiere el
        # género (el DLE no lo etiqueta); es el nombre del bucket de estilo solicitado.
        true_crime = self.documentary_style("true_crime", extra={
            "genre": "true_crime",
            "note": "género no inferido; agrega todo el corpus aprendido",
        })
        return {
            "true_crime": true_crime,
            "documentary_style": overall,
            "cinematography_patterns": cinematography,
            "editing_patterns": editing,
            "motion_patterns": motion,
            "lighting_patterns": lighting,
        }
