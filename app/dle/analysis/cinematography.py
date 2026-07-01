"""Ensambla el análisis de un plano (ShotAnalysis) a partir de sus fotogramas + audio.

Combina visual_style + motion + audio + narración. Los atributos que necesitan un
modelo (tamaño de plano, composición, rostro, nº de personas, interior/exterior) se
dejan en UNKNOWN: el DLE nunca inventa.
"""

from app.dle import UNKNOWN
from app.dle.analysis import audio as audio_an
from app.dle.analysis import narration as narration_an
from app.dle.analysis import visual_style
from app.dle.analysis.motion import analyze_motion
from app.dle.models import ShotAnalysis, Transcript


def analyze_shot(*, index: int, scene_index: int, start: float, end: float,
                 mid_frame: str | None, motion_frame: str | None,
                 silences: list[tuple[float, float]], has_audio: bool,
                 transcript: Transcript) -> ShotAnalysis:
    shot = ShotAnalysis(index=index, scene_index=scene_index, start=round(start, 3),
                        end=round(end, 3), duration=round(end - start, 3))

    if mid_frame:
        v = visual_style.analyze_frame(mid_frame)
        shot.brightness = v["brightness"]
        shot.contrast = v["contrast"]
        shot.color_temperature = v["color_temperature"]
        shot.dominant_color = v["dominant_color"]
        shot.lighting = v["lighting"]
        shot.day_night = v["day_night"]

    shot.motion_magnitude, shot.movement = analyze_motion(mid_frame, motion_frame)

    shot.audio_present = audio_an.audio_present(start, end, silences, has_audio)
    shot.music_present = audio_an.music_present()
    shot.effects_present = audio_an.effects_present()
    shot.narration_present = narration_an.narration_present(start, end, transcript)

    # Requieren detector/modelo -> UNKNOWN (no se inventan).
    shot.shot_size = UNKNOWN
    shot.composition = UNKNOWN
    shot.face_present = UNKNOWN
    shot.num_people = UNKNOWN
    shot.interior_exterior = UNKNOWN
    return shot
