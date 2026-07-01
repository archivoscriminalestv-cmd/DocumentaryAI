"""Tests de los adapters REALES del VPL (HTTP inyectado, sin red) + telemetría."""

import base64

import pytest

from app.vpl import ProviderError, VPLConfig, VisualGenerationOrchestrator
from app.vpl.adapters.flux import FluxProvider
from app.vpl.adapters.google_imagen import GoogleImagenProvider
from app.vpl.adapters.openai import OpenAIVisualProvider
from app.vpl.cache import AssetCache
from app.vpl.config import available_providers
from app.vpl.models import GenerationManifest
from app.vpl.telemetry import build_report
from app.vsc.models import VisualGenerationRequest

_PNG = b"\x89PNG\r\n\x1a\nIMAGEDATA"
_B64 = base64.b64encode(_PNG).decode()


def _req(shot_id="s1", prompt="a nuclear reactor at dusk", negative="cartoon, watermark", seed=7):
    return VisualGenerationRequest(
        shot_id=shot_id, scene_id="sc", media_type="image", prompt=prompt, negative_prompt=negative,
        global_style="g", scene_style="s", shot_style="sh", camera="Sony FX6", lens="35mm prime",
        lighting="soft", composition="thirds", color="muted", environment="Almassora", subject="Coquito",
        provider_constraints={"width": 1280, "height": 720, "aspect_ratio": "16:9"},
        reuse_key="", seed=seed, seed_strategy="per_scene", motion_hint="locked",
    )


# --- OpenAI ------------------------------------------------------------------

def test_openai_builds_request_and_parses(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "key-123")
    captured = {}

    def fake_post(url, body, headers, timeout):
        captured.update(url=url, body=body, headers=headers)
        return {"data": [{"b64_json": _B64}]}

    asset = OpenAIVisualProvider(http_post=fake_post).generate(_req())
    assert asset.provider == "openai" and asset.image_bytes == _PNG
    assert captured["body"]["model"] == "gpt-image-1"
    assert "a nuclear reactor at dusk" in captured["body"]["prompt"]
    assert "Avoid: cartoon, watermark" in captured["body"]["prompt"]   # negativos ejecutados
    assert captured["body"]["size"] == "1536x1024"                      # 16:9 -> landscape
    assert captured["headers"]["Authorization"] == "Bearer key-123"


def test_openai_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ProviderError):
        OpenAIVisualProvider(http_post=lambda *a: {}).generate(_req())


# --- Google Imagen -----------------------------------------------------------

def test_imagen_builds_request_and_parses(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "g-key")
    captured = {}

    def fake_post(url, body, headers, timeout):
        captured.update(url=url, body=body)
        return {"predictions": [{"bytesBase64Encoded": _B64}]}

    asset = GoogleImagenProvider(http_post=fake_post).generate(_req())
    assert asset.provider == "imagen" and asset.image_bytes == _PNG
    assert captured["body"]["instances"][0]["prompt"] == "a nuclear reactor at dusk"
    assert captured["body"]["parameters"]["negativePrompt"] == "cartoon, watermark"  # negative NATIVO
    assert captured["body"]["parameters"]["aspectRatio"] == "16:9"
    assert "key=g-key" in captured["url"] and "imagen" in captured["url"]


def test_imagen_missing_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(ProviderError):
        GoogleImagenProvider(http_post=lambda *a: {}).generate(_req())


# --- Flux (submit -> poll -> download) ---------------------------------------

def test_flux_submit_poll_download(monkeypatch):
    monkeypatch.setenv("FLUX_API_KEY", "f-key")
    captured = {}

    def fake_post(url, body, headers, timeout):
        captured.update(url=url, body=body, headers=headers)
        return {"id": "job-1", "polling_url": "http://poll/job-1"}

    def fake_get_json(url, headers, timeout):
        return {"status": "Ready", "result": {"sample": "http://img/job-1.png"}}

    def fake_get_bytes(url, headers, timeout):
        captured["image_url"] = url
        return _PNG

    provider = FluxProvider(http_post=fake_post, http_get_json=fake_get_json,
                            http_get_bytes=fake_get_bytes, sleep=lambda s: None)
    asset = provider.generate(_req())
    assert asset.provider == "flux" and asset.image_bytes == _PNG
    assert "a nuclear reactor at dusk" in captured["body"]["prompt"]
    assert captured["body"]["width"] == 1280 and captured["body"]["height"] == 720
    assert captured["body"]["seed"] == 7 and captured["headers"]["x-key"] == "f-key"
    assert captured["image_url"] == "http://img/job-1.png"


def test_flux_self_hosted_base_url(monkeypatch):
    monkeypatch.setenv("FLUX_API_KEY", "f")
    captured = {}
    provider = FluxProvider(base_url="http://localhost:9000/v1",
                            http_post=lambda url, *a: (captured.update(url=url) or {"id": "j"}),
                            http_get_json=lambda *a: {"status": "Ready", "result": {"sample": "u"}},
                            http_get_bytes=lambda *a: _PNG, sleep=lambda s: None)
    provider.generate(_req())
    assert captured["url"].startswith("http://localhost:9000/v1/")  # self-hosted configurable


def test_flux_failure_status(monkeypatch):
    monkeypatch.setenv("FLUX_API_KEY", "f")
    provider = FluxProvider(http_post=lambda *a: {"id": "j"},
                            http_get_json=lambda *a: {"status": "Error"},
                            http_get_bytes=lambda *a: _PNG, sleep=lambda s: None)
    with pytest.raises(ProviderError):
        provider.generate(_req())


def test_flux_missing_key(monkeypatch):
    monkeypatch.delenv("FLUX_API_KEY", raising=False)
    with pytest.raises(ProviderError):
        FluxProvider().generate(_req())


# --- disponibilidad + selección ----------------------------------------------

def test_available_providers(monkeypatch):
    for var in ("OPENAI_API_KEY", "GOOGLE_API_KEY", "FLUX_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    avail = available_providers()
    assert avail["mock"] is True and avail["openai"] is False and avail["imagen"] is False
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    assert available_providers()["openai"] is True


# --- telemetría --------------------------------------------------------------

def test_telemetry_report():
    manifest = GenerationManifest(
        documentary_id="d", provider="openai", model="gpt-image-1", timestamp="t",
        duration_seconds=12.5, total=2, cache_hits=1, cache_misses=1, failures=0, retries=1,
        assets=[{"status": "generated", "cost": 0.04, "generation_time": 3.0},
                {"status": "cached", "cost": 0.0, "generation_time": 0.0}],
        failed=[],
    )
    report = build_report(manifest)
    assert "Documentary generated" in report
    assert "Provider:           openai" in report and "Images:             2" in report
    assert "Cache reused:       1" in report and "$0.0400" in report
    assert "Average generation: 3.00s" in report


# --- graceful: falta de clave no bloquea el pipeline -------------------------

def test_orchestrator_graceful_when_provider_unconfigured(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    orch = VisualGenerationOrchestrator(
        config=VPLConfig(provider="openai", cache_dir=str(tmp_path / "c")),
        provider=OpenAIVisualProvider(), cache=AssetCache(str(tmp_path / "c")), sleep=lambda s: None,
    )
    manifest = orch.generate([_req("s1"), _req("s2")], documentary_id="d", output_dir=str(tmp_path / "out"))
    assert manifest.failures == 2 and manifest.assets == []          # no se bloquea
    assert all(f["status"] == "failed" for f in manifest.failed)
