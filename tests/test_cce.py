"""Tests del Character Consistency Engine (CCE) — deterministas, sin red."""

from dataclasses import dataclass

import pytest

from app.cce import (
    AttributeProfileComparator,
    CharacterProfile,
    IdentityConsistencyScorer,
    IdentityLockEngine,
    IdentityPromptBuilder,
    apply_identity,
    apply_identity_to_all,
    derive_continuity_rules,
)
from app.cce.models import VISUAL_ATTRIBUTES, visual_identity_id
from app.cre.models import (
    Behaviour,
    CharacterBible,
    Identity,
    PhysicalAppearance,
    VisualReference,
)


def _rich_bible(name="Nikola Tesla") -> CharacterBible:
    return CharacterBible(
        identity=Identity(canonical_name=name, nationality="Serbian-American"),
        physical_appearance=PhysicalAppearance(
            approximate_age="around 60", height="tall", body_type="slim", face_shape="oval",
            skin_tone="fair", eye_color="grey", hair="short black hair, neatly combed",
            beard="clean-shaven, thin moustache", clothing_style="formal three-piece suit",
            accessories=["pocket watch"]),
        behaviour=Behaviour(posture="upright", facial_expression="intense focused gaze",
                            movement_style="precise deliberate", personality=["intense", "meticulous"]),
        visual_references=[VisualReference(id="wc1", provider="commons", license="PD",
                                           url="http://x/1.jpg", quality_score=0.9)],
    )


def _partial_bible(name="Coquito") -> CharacterBible:
    return CharacterBible(identity=Identity(canonical_name=name))


# --- determinismo + identidad estable ----------------------------------------

def test_visual_identity_id_stable_and_name_based():
    assert visual_identity_id("Nikola Tesla") == visual_identity_id("Nikola Tesla")
    assert visual_identity_id("Nikola Tesla") != visual_identity_id("Marie Curie")
    assert visual_identity_id("Tesla").startswith("vid_")


def test_lock_is_deterministic():
    eng = IdentityLockEngine()
    a = eng.lock(_rich_bible())
    b = eng.lock(_rich_bible())
    assert a.to_dict() == b.to_dict()


def test_lock_maps_physical_and_behaviour():
    p = IdentityLockEngine().lock(_rich_bible())
    assert p.canonical_name == "Nikola Tesla"
    assert p.skin_tone == "fair" and p.eye_color == "grey" and p.face_shape == "oval"
    assert p.facial_hair.startswith("clean-shaven")
    assert p.posture == "upright" and p.walking_style == "precise deliberate"
    assert p.hair_color == "black"            # extraído del texto de 'hair'
    assert p.age_range == "60s"               # bucket determinista desde 'around 60'
    assert p.completeness > 0.5


# --- perfiles parciales (Coquito): nunca inventar ----------------------------

def test_partial_profile_invents_nothing():
    p = IdentityLockEngine().lock(_partial_bible())
    assert p.canonical_name == "Coquito" and p.visual_identity_id.startswith("vid_")
    assert p.completeness == 0.0
    assert p.attribute_values() == {}          # ningún rasgo inventado
    assert p.visual_constraints == []
    # Pero SÍ existen reglas de estabilidad de identidad (no inventan rasgos).
    attrs = {r.attribute for r in p.continuity_rules}
    assert "identity" in attrs and "face_proportions" in attrs


# --- continuity rules derivadas ----------------------------------------------

def test_continuity_rules_locked_vs_soft():
    p = IdentityLockEngine().lock(_rich_bible())
    rules = {r.attribute: r for r in p.continuity_rules}
    assert rules["eye_color"].severity == "locked"
    assert rules["clothing_style"].severity == "soft"     # la ropa puede evolucionar
    assert rules["accessories"].severity == "soft"
    # Las reglas se derivan (no se escriben a mano): coinciden con el perfil.
    assert derive_continuity_rules(p)[0].attribute == "identity"


# --- prompt builder ----------------------------------------------------------

def test_prompt_block_built_from_profile():
    p = IdentityLockEngine().lock(_rich_bible())
    block = IdentityPromptBuilder().build_identity_block(p)
    assert "the same person, Nikola Tesla" in block
    assert "the same eye colour (grey)" in block
    assert "do not redesign the character" in block
    assert p.visual_identity_id in block


def test_prompt_block_partial_has_only_stability():
    p = IdentityLockEngine().lock(_partial_bible())
    block = IdentityPromptBuilder().build_identity_block(p)
    assert "the same person, Coquito" in block
    assert "maintain identity consistency" in block
    # Sin rasgos concretos inventados.
    assert "eye colour" not in block and "skin tone" not in block


# --- independencia de proveedor ----------------------------------------------

def test_profile_is_provider_agnostic():
    p = IdentityLockEngine().lock(_rich_bible())
    blob = (str(p.to_dict()) + IdentityPromptBuilder().build_identity_block(p)).lower()
    for token in ("imagen", "flux", "sdxl", "midjourney", "stable diffusion",
                  "dall-e", "--ar", "openai", "replicate", "huggingface"):
        assert token not in blob


# --- serialización + versionado ----------------------------------------------

def test_serialization_roundtrip_and_version():
    p = IdentityLockEngine().lock(_rich_bible())
    restored = CharacterProfile.from_dict(p.to_dict())
    assert restored.to_dict() == p.to_dict()
    assert restored.schema_version == p.schema_version
    assert restored.reference_images[0].provider == "commons"
    assert restored.continuity_rules[0].attribute == "identity"


# --- consistency score -------------------------------------------------------

def test_score_same_profile_is_one():
    p = IdentityLockEngine().lock(_rich_bible())
    assert IdentityConsistencyScorer().score(p, p).score == 1.0


def test_score_detects_different_person():
    a = IdentityLockEngine().lock(_rich_bible("Nikola Tesla"))
    b = IdentityLockEngine().lock(_rich_bible("Marie Curie"))
    # Mismos atributos textuales pero distinto id -> el comparador marca diferencias
    # solo si difieren valores; aquí valores iguales => score alto, pero id distinto.
    result = IdentityConsistencyScorer().score(a, b)
    assert result.same_identity_id is False


def test_score_mismatched_attributes_lower():
    a = IdentityLockEngine().lock(_rich_bible())
    bible_b = _rich_bible()
    bible_b.physical_appearance.eye_color = "brown"
    bible_b.physical_appearance.skin_tone = "dark"
    b = IdentityLockEngine().lock(bible_b)
    result = AttributeProfileComparator().compare(a, b)
    assert result.score < 1.0 and "eye_color" in result.mismatched


# --- integración (contrato aditivo) ------------------------------------------

@dataclass
class _Req:
    shot_id: str = "s1"
    prompt: str = "wide shot of the street corner"
    negative_prompt: str = "blurry"


def test_apply_identity_prepends_block_and_merges_negatives():
    p = IdentityLockEngine().lock(_rich_bible())
    out = apply_identity(_Req(), p)
    assert out.prompt.startswith("Consistent identity")
    assert "wide shot of the street corner" in out.prompt      # prompt del plano intacto
    assert "blurry" in out.negative_prompt and "different person" in out.negative_prompt
    assert out is not None


def test_apply_identity_to_all_is_consistent():
    p = IdentityLockEngine().lock(_rich_bible())
    reqs = [_Req(shot_id=f"s{i}", prompt=f"shot {i}") for i in range(26)]
    out = apply_identity_to_all(reqs, p)
    blocks = {r.prompt.split(". ")[0] for r in out}
    assert len(out) == 26
    assert len(blocks) == 1                                     # idéntico bloque en los 26


def test_apply_identity_does_not_mutate_original():
    p = IdentityLockEngine().lock(_rich_bible())
    original = _Req()
    apply_identity(original, p)
    assert original.prompt == "wide shot of the street corner"  # sin mutación
