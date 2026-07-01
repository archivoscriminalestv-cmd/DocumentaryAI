"""DirectorService — dirige el documental: Scene[] -> DirectedScene[] (Sprint C-08).

NO escribe ni inventa: solo REORDENA, ANOTA (duration_hint/emphasis/tone) y deja
pasar ``fact_ids``, ``title`` y ``narration`` sin cambios de significado.

Como la ``Scene`` no trae el tipo de relación, se infiere de forma determinista
la categoría dominante a partir de las señales que C-07 deja en el título y la
narración (con un valor por defecto seguro). De la categoría se derivan:

- orden narrativo: causal -> temporal -> geográfico -> jerárquico -> asociativo
  (gancho/escalada causal primero; síntesis al final),
- ``duration_hint`` (peso narrativo), ``emphasis`` (intensidad), ``tone``.

El tono respeta posición: la primera escena es el gancho ("investigative") y la
última, el cierre ("conclusive").
"""

from app.domain.narrative.directed_scene import DirectedScene

# Señales deterministas (título + narración) -> categoría, en orden de prioridad.
_SIGNALS: list[tuple[str, tuple[str, ...]]] = [
    ("causal", ("causal", "as a consequence", "led to", "because", "caused",
                "resulted in", "consequence", "why ")),
    ("temporal", ("timeline", "sequence", "subsequently", "chronolog")),
    ("hierarchical", ("bigger picture", "fits into", "fit together",
                      "more broadly", "part of", "type of", "hierarch")),
    ("geographical", ("setting", "geograph", "location", "region")),
    ("associative", ("connections", "connection", "relatedly", "related",
                     "links", "associat", "surrounding")),
]

_ORDER_RANK = {"causal": 0, "temporal": 1, "geographical": 2, "hierarchical": 3, "associative": 4}
_EMPHASIS = {"causal": 0.9, "temporal": 0.6, "hierarchical": 0.6, "geographical": 0.5, "associative": 0.35}
_DURATION = {"causal": 4.0, "temporal": 2.5, "hierarchical": 2.5, "geographical": 1.2, "associative": 1.0}
_BASE_TONE = {
    "causal": "dramatic",
    "temporal": "explanatory",
    "hierarchical": "explanatory",
    "geographical": "neutral",
    "associative": "neutral",
}


def _category(scene) -> str:
    text = (str(getattr(scene, "title", "")) + " " + str(getattr(scene, "narration", ""))).lower()
    for category, signals in _SIGNALS:
        if any(sig in text for sig in signals):
            return category
    return "associative"  # por defecto: contexto/glue de fondo


class DirectorService:
    def direct(self, scenes: list) -> list[DirectedScene]:
        valid = [s for s in (scenes or []) if getattr(s, "id", None) is not None]
        if not valid:
            return []

        categorized = [(scene, _category(scene)) for scene in valid]

        # Reordenar por flujo narrativo (estable dentro de cada categoría).
        ordered = sorted(
            enumerate(categorized),
            key=lambda pair: (_ORDER_RANK[pair[1][1]], pair[0]),
        )

        total = len(ordered)
        directed: list[DirectedScene] = []
        for position, (_, (scene, category)) in enumerate(ordered):
            directed.append(
                DirectedScene(
                    id=str(scene.id),
                    title=str(getattr(scene, "title", "")),          # sin cambios
                    narration=str(getattr(scene, "narration", "")),  # sin cambios
                    fact_ids=list(getattr(scene, "fact_ids", []) or []),  # intacto
                    duration_hint=_DURATION[category],
                    emphasis=_EMPHASIS[category],
                    tone=self._tone(category, position, total),
                )
            )
        return directed

    @staticmethod
    def _tone(category: str, position: int, total: int) -> str:
        if total > 1:
            if position == 0:
                return "investigative"   # gancho/anomalía
            if position == total - 1:
                return "conclusive"      # cierre/síntesis
        return _BASE_TONE.get(category, "neutral")
