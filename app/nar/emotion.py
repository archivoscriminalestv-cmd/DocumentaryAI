"""Diseñador de la curva emocional (NAR-001).

Asigna emoción y tensión a cada segmento partiendo del catálogo de beats y ajustándolas por
género (reglas objetivas, sin opinión). Después deduce la FORMA del arco a partir de la
secuencia de tensión. No escribe nada: solo símbolos del vocabulario.
"""

from app.nar.models import EmotionCurve, EmotionPoint, NarrativeContext, NarrativeSegment
from app.nar.vocabulary import ArcType, Emotion, TensionLevel

# Suelo emocional por género: si un beat es NEUTRAL, el género le da color.
_GENRE_FLOOR = {
    "true_crime": Emotion.UNEASE,
    "nature": Emotion.AWE,
}


class EmotionCurveDesigner:
    def design(self, context: NarrativeContext,
               segments: list[NarrativeSegment]) -> EmotionCurve:
        floor = _GENRE_FLOOR.get(context.genre)
        points: list[EmotionPoint] = []
        for seg in segments:
            if floor and seg.emotion == Emotion.NEUTRAL:
                seg.emotion = floor
            intensity = round(TensionLevel.RANK.get(seg.tension, 0) / 4.0, 4)
            points.append(EmotionPoint(index=seg.index, segment_id=seg.id,
                                       emotion=seg.emotion, tension=seg.tension,
                                       intensity=intensity))
        ranks = [TensionLevel.RANK.get(s.tension, 0) for s in segments]
        arc, peak = self._arc(ranks)
        return EmotionCurve(arc_type=arc, points=points, peak_index=peak,
                            summary=self._summary(arc, peak, len(segments)))

    @staticmethod
    def _arc(ranks: list[int]) -> tuple[str, int]:
        if not ranks:
            return ArcType.FLAT, -1
        hi, lo = max(ranks), min(ranks)
        peak = ranks.index(hi)
        if hi == lo:
            return ArcType.FLAT, peak
        if ranks.count(hi) >= 3:
            return ArcType.OSCILLATING, peak
        n = len(ranks)
        if peak >= 0.6 * (n - 1):
            return ArcType.STEADY_BUILD, peak
        if peak <= 0.3 * (n - 1):
            # arranca alto: tragedia si termina bajo, recuperación si termina alto
            return (ArcType.TRAGIC if ranks[-1] <= lo else ArcType.FALL_RISE), peak
        return ArcType.RISE_FALL, peak

    @staticmethod
    def _summary(arc: str, peak: int, n: int) -> str:
        return f"arco {arc}; pico de tensión en el segmento {peak} de {n}"
