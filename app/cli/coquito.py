"""Documental de ejemplo "Coquito" (fuente compartida por VSC y VPL).

Define las escenas (narrativa + SceneVisualContext + duración) cuyo total de
planos es 26 (8+6+6+6) para la demostración del Visual Provider Layer. La escena
final regresa a la misma localización (``corner_finestrelles_almassora``) para
demostrar la reutilización de localizaciones por la caché.
"""

from app.vsc import SceneVisualContext
from app.domain.narrative.scene import Scene

_CONSTRAINTS = {"width": 1280, "height": 720, "aspect_ratio": "16:9"}


def _ctx(scene_id, identity, location, time_of_day, weather, doc_style, seed) -> SceneVisualContext:
    return SceneVisualContext(
        scene_id=scene_id, identity=identity, location=location, season="January",
        time_of_day=time_of_day, weather=weather, color_palette="muted cold tones",
        camera_package="Sony FX6", lens_family="35mm prime",
        lighting_language="soft overcast natural light", documentary_style=doc_style,
        realism_level="high", provider_constraints=_CONSTRAINTS,
        negative_prompts=("toy-like", "stylized"), seed_strategy="per_scene", seed=seed,
        reuse_policy="shot",
    )


def coquito_documentary() -> list[tuple[Scene, SceneVisualContext, float]]:
    """(Scene, SceneVisualContext, scene_duration) — 4 escenas, 26 planos."""
    return [
        (
            Scene(id="scene-01", title="Coquito at home",
                  narration="Coquito spends the cold January afternoon by the window of the flat.", fact_ids=["f1"]),
            _ctx("scene-01", "coquito_home", "a small flat in Almassora, Spain", "afternoon",
                 "overcast", "intimate documentary", 1001),
            24.0,  # -> 8 planos
        ),
        (
            Scene(id="scene-02", title="The corner of Finestrelles",
                  narration="Every morning Coquito walks to the same corner of Carrer Finestrelles under light rain.", fact_ids=["f2"]),
            _ctx("scene-02", "corner_finestrelles_almassora", "the corner of Carrer Finestrelles, Almassora",
                 "morning", "light rain", "observational documentary", 1002),
            18.0,  # -> 6 planos
        ),
        (
            Scene(id="scene-03", title="The neighborhood market",
                  narration="At the market the vendors already know Coquito and his quiet routine.", fact_ids=["f3"]),
            _ctx("scene-03", "almassora_market", "a small neighborhood market in Almassora",
                 "midday", "overcast", "observational documentary", 1003),
            18.0,  # -> 6 planos
        ),
        (
            Scene(id="scene-04", title="Back to the corner",
                  narration="By dusk Coquito returns to the same corner, the light now fading.", fact_ids=["f4"]),
            _ctx("scene-04", "corner_finestrelles_almassora", "the corner of Carrer Finestrelles, Almassora",
                 "dusk", "light rain", "reflective documentary", 1002),
            18.0,  # -> 6 planos (localización reutilizada)
        ),
    ]
