"""StyleEngine — Style & Prompt Intelligence Layer (Fase A).

Convierte escenas simples en prompts visuales cinematográficos CONSISTENTES, de
forma puramente determinista (reglas + plantillas, sin IA, sin embeddings).

- Registry de estilos globales (documentary, cinematic, youtube_documentary,
  nature_doc, investigative_report); cada uno con prefijo, descriptores visuales,
  reglas de iluminación y lenguaje de cámara.
- ``enrich_prompt(scene, style)``: escena simple -> prompt enriquecido (estilo +
  cámara + iluminación + coherencia documental), sin perder el sujeto base.
- Visual Consistency Lock: ``StyleSession`` fija 1 ``style_id`` por vídeo para que
  TODAS las escenas compartan la misma estética.

No depende del MGL ni de providers.
"""

from dataclasses import dataclass

# Coherencia documental común a todos los estilos (clave de consistencia global).
_COHERENCE = (
    "cohesive visual style, consistent color grading, professional documentary "
    "cinematography, highly detailed, photorealistic"
)


@dataclass(frozen=True)
class VisualStyle:
    style_id: str
    prefix: str                  # prompt prefix
    descriptors: tuple[str, ...]  # visual descriptors
    lighting: str                # lighting rules
    camera: str                  # camera language hints


_REGISTRY: dict[str, VisualStyle] = {
    "documentary": VisualStyle(
        style_id="documentary",
        prefix="documentary photography",
        descriptors=("realistic", "authentic", "natural color grading", "true-to-life detail"),
        lighting="soft natural lighting",
        camera="35mm lens, shallow depth of field, eye-level framing",
    ),
    "cinematic": VisualStyle(
        style_id="cinematic",
        prefix="cinematic film still",
        descriptors=("dramatic composition", "high dynamic range", "filmic color grade", "atmospheric"),
        lighting="moody chiaroscuro lighting, golden hour",
        camera="anamorphic 35mm lens, shallow depth of field, wide establishing shot",
    ),
    "youtube_documentary": VisualStyle(
        style_id="youtube_documentary",
        prefix="modern youtube documentary still",
        descriptors=("clean", "high contrast", "vivid yet realistic", "engaging composition"),
        lighting="bright balanced lighting",
        camera="35mm lens, medium shot, rule-of-thirds framing",
    ),
    "nature_doc": VisualStyle(
        style_id="nature_doc",
        prefix="nature documentary still",
        descriptors=("lush detail", "vibrant natural tones", "pristine wildlife realism"),
        lighting="soft golden natural light",
        camera="telephoto lens, shallow depth of field, sweeping wide shot",
    ),
    "investigative_report": VisualStyle(
        style_id="investigative_report",
        prefix="investigative report still",
        descriptors=("gritty realism", "desaturated tones", "tense serious mood", "evidentiary detail"),
        lighting="low-key dramatic lighting, hard shadows",
        camera="35mm lens, deep focus, handheld eye-level framing",
    ),
}

_DEFAULT_STYLE = "documentary"


def _base_text(scene) -> str:
    if isinstance(scene, str):
        text = scene
    else:
        text = str(getattr(scene, "image_prompt", "") or "")
        if not text:
            title = str(getattr(scene, "title", ""))
            narration = str(getattr(scene, "narration", ""))
            text = f"{title}. {narration}".strip(". ").strip()
    return " ".join(text.split())


class StyleEngine:
    def __init__(self, registry: dict[str, VisualStyle] | None = None) -> None:
        self._registry = dict(registry or _REGISTRY)

    def available_styles(self) -> list[str]:
        return sorted(self._registry)

    def get_style(self, style: str) -> VisualStyle:
        return self._registry.get(self._normalize(style), self._registry[_DEFAULT_STYLE])

    @staticmethod
    def _normalize(style: str) -> str:
        return str(style or "").strip().lower()

    def enrich_prompt(self, scene, style: str) -> str:
        """Escena simple -> prompt cinematográfico enriquecido y consistente."""
        style_def = self.get_style(style)
        base = _base_text(scene)
        segments = [
            style_def.prefix,
            base,
            style_def.camera,
            style_def.lighting,
            ", ".join(style_def.descriptors),
            _COHERENCE,
        ]
        return ", ".join(seg.strip() for seg in segments if seg and seg.strip())

    def session(self, style: str) -> "StyleSession":
        """Bloquea un estilo para todo un vídeo (Visual Consistency Lock)."""
        return StyleSession(self, style)


class StyleSession:
    """Sesión de vídeo con UN único estilo: todas las escenas lo comparten."""

    def __init__(self, engine: StyleEngine, style: str) -> None:
        self._engine = engine
        self.style_id = engine.get_style(style).style_id  # estilo resuelto y fijo

    def enrich(self, scene) -> str:
        return self._engine.enrich_prompt(scene, self.style_id)


# Conveniencia: motor por defecto + función con la firma del sprint.
_DEFAULT_ENGINE = StyleEngine()


def enrich_prompt(scene, style: str) -> str:
    return _DEFAULT_ENGINE.enrich_prompt(scene, style)
