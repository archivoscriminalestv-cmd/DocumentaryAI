"""Tests de los adapters HF + Replicate (HTTP inyectado, sin red)."""

import pytest

from app.vpl.adapters.huggingface import HuggingFaceProvider, _clamp_dims
from app.vpl.adapters.replicate import ReplicateProvider
from app.vpl.provider import ProviderError
from app.vsc.models import VisualGenerationRequest

_PNG = b"\x89PNG\r\n\x1a\n" + b"x" * 2048


def _req(shot_id="s1", prompt="a documentary photograph of a street", negative="cartoon, anime", seed=7):
    return VisualGenerationRequest(
        shot_id=shot_id, scene_id="sc", media_type="image", prompt=prompt, negative_prompt=negative,
        global_style="g", scene_style="s", shot_style="sh", camera="FX6", lens="35mm",
        lighting="soft", composition="thirds", color="muted", environment="Almassora", subject="Coquito",
        provider_constraints={"width": 1280, "height": 720, "aspect_ratio": "16:9"},
        reuse_key="", seed=seed, seed_strategy="per_scene", motion_hint="locked",
    )


# --- Hugging Face ------------------------------------------------------------

def test_hf_sends_exact_prompt_and_parses(monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "hf-key")
    captured = {}

    def fake_post_bytes(url, body, headers, timeout):
        captured.update(url=url, body=body, headers=headers)
        return _PNG, "image/png"

    asset = HuggingFaceProvider(http_post_bytes=fake_post_bytes).generate(_req())
    assert asset.provider == "huggingface" and asset.image_bytes == _PNG
    assert captured["body"]["inputs"] == "a documentary photograph of a street"   # prompt EXACTO
    assert captured["body"]["parameters"]["negative_prompt"] == "cartoon, anime"
    assert captured["headers"]["Authorization"] == "Bearer hf-key"
    assert "router.huggingface.co" in captured["url"]                             # nuevo endpoint
    assert "FLUX.1-schnell" in captured["url"]                                    # mejor modelo servido


def test_hf_model_fallback_on_error(monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "hf")
    seen = []

    def fake_post_bytes(url, body, headers, timeout):
        seen.append(url)
        if "FLUX.1-schnell" in url:
            raise ProviderError("HTTP 410: deprecated", transient=False)
        return _PNG, "image/png"

    asset = HuggingFaceProvider(http_post_bytes=fake_post_bytes).generate(_req())
    assert asset.model == "black-forest-labs/FLUX.1-dev"         # cayó al siguiente modelo
    assert len(seen) == 2


def test_hf_missing_token(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    with pytest.raises(ProviderError):
        HuggingFaceProvider(http_post_bytes=lambda *a: (_PNG, "image/png")).generate(_req())


def test_hf_clamp_dims_preserves_ratio():
    w, h = _clamp_dims(1280, 720, max_side=1024)
    assert w == 1024 and h == 576 and w % 8 == 0 and h % 8 == 0


# --- Replicate ---------------------------------------------------------------

def test_replicate_submit_poll_download(monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "r8-key")
    captured = {}

    def fake_post(url, body, headers, timeout):
        captured.update(url=url, body=body, headers=headers)
        return {"status": "processing", "urls": {"get": "http://poll/1"}}

    def fake_get_json(url, headers, timeout):
        return {"status": "succeeded", "output": ["http://img/1.png"]}

    def fake_get_bytes(url, headers, timeout):
        captured["image_url"] = url
        return _PNG

    provider = ReplicateProvider(http_post=fake_post, http_get_json=fake_get_json,
                                 http_get_bytes=fake_get_bytes, sleep=lambda s: None)
    asset = provider.generate(_req())
    assert asset.provider == "replicate" and asset.image_bytes == _PNG
    assert captured["body"]["input"]["prompt"] == "a documentary photograph of a street"  # EXACTO
    assert captured["body"]["input"]["aspect_ratio"] == "16:9"
    assert captured["headers"]["Authorization"] == "Bearer r8-key"
    assert "flux-dev" in captured["url"]
    assert captured["image_url"] == "http://img/1.png"


def test_replicate_immediate_success(monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "r8")
    provider = ReplicateProvider(
        http_post=lambda *a: {"status": "succeeded", "output": ["http://img/x.png"]},
        http_get_json=lambda *a: {}, http_get_bytes=lambda *a: _PNG, sleep=lambda s: None)
    asset = provider.generate(_req())
    assert asset.image_bytes == _PNG


def test_replicate_failed_status(monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "r8")
    provider = ReplicateProvider(
        http_post=lambda *a: {"status": "failed", "error": "nope", "urls": {"get": "u"}},
        http_get_json=lambda *a: {"status": "failed", "error": "nope"},
        http_get_bytes=lambda *a: _PNG, sleep=lambda s: None)
    with pytest.raises(ProviderError):
        provider.generate(_req())


def test_replicate_missing_token(monkeypatch):
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    with pytest.raises(ProviderError):
        ReplicateProvider().generate(_req())
