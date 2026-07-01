"""Tests del Style & Prompt Intelligence Layer (Fase A). Determinista, sin IA."""

from app.media.generation.mgl import MediaGenerationLayer
from app.media.generation.provider_router import ProviderRouter
from app.media.providers.base import BaseProvider
from app.media.store.asset_store import AssetStore
from app.media.styles.style_engine import StyleEngine, enrich_prompt
from app.domain.narrative.scene import Scene

_STYLES = ["documentary", "cinematic", "youtube_documentary", "nature_doc", "investigative_report"]


def _scene(id_, title, narration="") -> Scene:
    return Scene(id=id_, title=title, narration=narration, fact_ids=[])


# --- enrich_prompt: determinismo, consistencia, cambio de estilo -------------

def test_registry_contains_all_required_styles():
    assert set(StyleEngine().available_styles()) == set(_STYLES)


def test_same_scene_same_style_is_deterministic():
    engine = StyleEngine()
    scene = _scene("s1", "A nuclear reactor at night")
    assert engine.enrich_prompt(scene, "cinematic") == engine.enrich_prompt(scene, "cinematic")


def test_enriched_prompt_keeps_base_subject_and_adds_film_language():
    engine = StyleEngine()
    out = engine.enrich_prompt(_scene("s1", "A nuclear reactor at night"), "documentary")
    assert "nuclear reactor at night" in out          # no se pierde el sujeto
    assert "35mm" in out and "depth of field" in out   # lenguaje de cámara
    assert "lighting" in out                            # iluminación
    assert len(out) > len("A nuclear reactor at night") # prompt más rico


def test_different_scenes_same_style_share_visual_keywords():
    engine = StyleEngine()
    a = engine.enrich_prompt(_scene("s1", "A reactor control room"), "cinematic")
    b = engine.enrich_prompt(_scene("s2", "A quiet abandoned town"), "cinematic")
    style = engine.get_style("cinematic")
    # Misma estética: prefijo, cámara, iluminación y descriptores en ambas.
    for token in (style.prefix, style.camera, style.lighting, *style.descriptors):
        assert token in a and token in b


def test_changing_style_changes_output_clearly():
    engine = StyleEngine()
    scene = _scene("s1", "A reactor control room")
    doc = engine.enrich_prompt(scene, "documentary")
    cine = engine.enrich_prompt(scene, "cinematic")
    assert doc != cine
    assert engine.get_style("cinematic").prefix in cine
    assert engine.get_style("cinematic").prefix not in doc


def test_unknown_style_falls_back_deterministically():
    engine = StyleEngine()
    scene = _scene("s1", "A reactor")
    out = engine.enrich_prompt(scene, "does-not-exist")
    assert out == engine.enrich_prompt(scene, "documentary")  # fallback estable


def test_module_level_enrich_prompt_matches_engine():
    scene = _scene("s1", "A reactor")
    assert enrich_prompt(scene, "nature_doc") == StyleEngine().enrich_prompt(scene, "nature_doc")


# --- Visual Consistency Lock (1 estilo por vídeo) ----------------------------

def test_style_session_locks_one_style_across_scenes():
    session = StyleEngine().session("investigative_report")
    assert session.style_id == "investigative_report"
    a = session.enrich(_scene("s1", "A reactor"))
    b = session.enrich(_scene("s2", "A town"))
    assert "investigative report still" in a and "investigative report still" in b


# --- Integración MGL ---------------------------------------------------------

class _EchoProvider(BaseProvider):
    """Devuelve un Asset cuyo prompt es exactamente el recibido (para inspección)."""
    name = "echo"

    def __init__(self):
        self.seen: list[str] = []
        self._n = 0

    def generate_image(self, prompt: str):
        from app.media.store.models import Asset
        self.seen.append(prompt)
        self._n += 1
        return Asset(asset_id=f"a{self._n}", type="image", prompt=prompt, provider=self.name)

    def generate_video(self, prompt: str):
        raise NotImplementedError


def test_mgl_applies_style_before_provider(tmp_path):
    provider = _EchoProvider()
    mgl = MediaGenerationLayer(
        router=ProviderRouter(image_providers=[provider]),
        store=AssetStore(base_dir=str(tmp_path)),
        style_engine=StyleEngine(),
        style="cinematic",
    )
    asset = mgl.generate_for_scene(_scene("s1", "A nuclear reactor at night"))
    # el prompt que llega al provider está enriquecido con el estilo
    assert "cinematic film still" in provider.seen[0]
    assert "nuclear reactor at night" in provider.seen[0]
    assert asset.prompt == provider.seen[0]  # se persiste el prompt enriquecido


def test_mgl_without_style_keeps_base_prompt(tmp_path):
    provider = _EchoProvider()
    mgl = MediaGenerationLayer(
        router=ProviderRouter(image_providers=[provider]),
        store=AssetStore(base_dir=str(tmp_path)),
    )
    mgl.generate_for_scene(_scene("s1", "A nuclear reactor at night"))
    assert provider.seen[0] == "A nuclear reactor at night"  # comportamiento previo intacto
