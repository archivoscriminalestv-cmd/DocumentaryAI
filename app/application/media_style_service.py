"""MediaStyleService — Media Style Engine (Sprint C-09).

Transforma ``DirectedScene[]`` en ``MediaStyledScene[]`` definiendo la identidad
audiovisual del CANAL (voz, estilo visual, prompt de imagen, música, intro) de
forma DETERMINISTA y consistente. NO usa IA. NO modifica narration/title/fact_ids
ni inventa hechos: solo ENRIQUECE con metadatos de media.

Consistencia: una sola identidad de voz para todas las escenas; misma cámara,
composición, estilo y realismo en todo el canal. Solo la iluminación, la paleta,
el prompt de imagen y la música varían según el ``tone`` de cada escena. La intro
del canal se inyecta únicamente en la primera escena.
"""

import json
from dataclasses import asdict

from app.domain.media import (
    IntroInjection,
    MediaStyledScene,
    VisualStyle,
    VoiceProfile,
)

# tone -> música (sin estilos comerciales/pop/upbeat).
_MUSIC_BY_TONE = {
    "investigative": "subtle tension ambient",
    "explanatory": "minimal neutral ambient",
    "dramatic": "low-frequency cinematic tension",
    "neutral": "soft atmospheric pad",
    "conclusive": "resolved orchestral ambient",
}
_DEFAULT_MUSIC = "soft atmospheric pad"

# tone -> (iluminación, paleta). Resto del estilo visual = identidad de canal.
_VISUAL_BY_TONE = {
    "investigative": ("moody low-key cinematic", "cold muted"),
    "explanatory": ("neutral cinematic", "neutral muted"),
    "dramatic": ("moody high-contrast cinematic", "cold muted"),
    "neutral": ("natural cinematic", "muted"),
    "conclusive": ("warm cinematic", "warm muted"),
}
_DEFAULT_VISUAL = ("natural cinematic", "muted")

_INTRO_DURATION = 5.0  # dentro del rango 3-7s


class MediaStyleService:
    def __init__(
        self,
        language: str = "es",
        gender: str = "neutral",
        accent: str = "",
        pace: str = "moderate",
    ) -> None:
        # Configuración de canal: define la única identidad de voz.
        self._language = language
        self._gender = gender
        self._accent = accent
        self._pace = pace

    def style(self, scenes: list) -> list[MediaStyledScene]:
        valid = [s for s in (scenes or []) if getattr(s, "id", None) is not None]
        styled: list[MediaStyledScene] = []
        for index, scene in enumerate(valid):
            tone = str(getattr(scene, "tone", "neutral") or "neutral")
            lighting, palette = _VISUAL_BY_TONE.get(tone, _DEFAULT_VISUAL)
            title = str(getattr(scene, "title", ""))
            narration = str(getattr(scene, "narration", ""))
            styled.append(
                MediaStyledScene(
                    id=str(scene.id),
                    title=title,  # sin cambios
                    narration=narration,  # sin cambios
                    fact_ids=list(getattr(scene, "fact_ids", []) or []),  # intacto
                    voice_profile=self._voice_profile(),  # misma identidad
                    visual_style=VisualStyle(lighting=lighting, color_palette=palette),
                    image_prompt=self._image_prompt(title, narration, lighting),
                    music_style=_MUSIC_BY_TONE.get(tone, _DEFAULT_MUSIC),
                    intro=self._intro(index),
                )
            )
        return styled

    def _voice_profile(self) -> VoiceProfile:
        # Una nueva instancia por escena (sin estado compartido) pero con los
        # mismos valores: la voz es idéntica en todo el canal.
        return VoiceProfile(
            language=self._language,
            gender=self._gender,
            accent=self._accent,
            pace=self._pace,
        )

    @staticmethod
    def _intro(index: int) -> IntroInjection | None:
        if index == 0:
            return IntroInjection(
                type="video",
                asset="channel_intro.mp4",
                duration=_INTRO_DURATION,
                transition="fade_to_scene",
            )
        return None

    @staticmethod
    def _image_prompt(title: str, narration: str, lighting: str) -> str:
        # El sujeto se ancla en la escena (título/narración); no se inventan hechos.
        subject = (title or narration).strip().replace("\n", " ")
        if len(subject) > 140:
            subject = subject[:140].rstrip() + "..."
        if not subject:
            subject = "the documentary subject"
        return (
            f"cinematic documentary shot of {subject}, {lighting}, "
            "shallow depth of field, slow zoom, atmospheric realism, "
            "archival film texture, 4k film still, no text, no overlays, no infographics"
        )


def to_json(scenes: list[MediaStyledScene]) -> str:
    """Serializa MediaStyledScene[] a JSON válido (intro = null cuando no aplica)."""
    return json.dumps([asdict(scene) for scene in scenes], ensure_ascii=False, indent=2)
