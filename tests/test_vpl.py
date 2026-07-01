"""Tests del Visual Provider Layer (VPL). Mock determinista; sin red."""

import json
import os

import pytest

from app.vpl import GeneratedAsset, ProviderError, VisualGenerationOrchestrator, VPLConfig, build_provider
from app.vpl.adapters import FluxProvider, MockVisualProvider, OpenAIVisualProvider
from app.vpl.cache import AssetCache
from app.vpl.queue import WorkerPool
from app.vpl.retry import run_with_retry
from app.vsc.models import VisualGenerationRequest


def _req(shot_id="s1", scene_id="sc", prompt="a cat on a roof", reuse_key="", seed=1):
    return VisualGenerationRequest(
        shot_id=shot_id, scene_id=scene_id, media_type="image", prompt=prompt, negative_prompt="bad",
        global_style="g", scene_style="s", shot_style="sh", camera="Sony FX6", lens="35mm prime",
        lighting="soft overcast", composition="rule of thirds", color="muted cold tones",
        environment="Almassora", subject="Coquito",
        provider_constraints={"width": 320, "height": 180, "aspect_ratio": "16:9"},
        reuse_key=reuse_key, seed=seed, seed_strategy="per_scene", motion_hint="locked",
    )


_FAKE_PNG = b"\x89PNG\r\n\x1a\nFAKEDATA"


class _Flaky:
    name = "flaky"; model = "m1"

    def __init__(self, fail_times=0):
        self.fail = fail_times; self.calls = 0

    def generate(self, request):
        self.calls += 1
        if self.calls <= self.fail:
            raise ProviderError("temporary", transient=True)
        return GeneratedAsset(shot_id=request.shot_id, scene_id=request.scene_id, provider=self.name,
                              model=self.model, prompt=request.prompt, negative_prompt=request.negative_prompt,
                              seed=request.seed, width=10, height=10, image_bytes=_FAKE_PNG)


class _Broken:
    name = "broken"; model = "m"

    def generate(self, request):
        raise ProviderError("permanent", transient=False)


# --- provider interface + mock ----------------------------------------------

def test_mock_provider_generates_real_png():
    asset = MockVisualProvider().generate(_req())
    assert asset.provider == "mock" and asset.image_bytes[:4] == b"\x89PNG"
    assert asset.width == 320 and asset.height == 180


def test_provider_selection_by_config():
    assert isinstance(build_provider(VPLConfig(provider="mock")), MockVisualProvider)
    assert isinstance(build_provider(VPLConfig(provider="openai")), OpenAIVisualProvider)
    assert isinstance(build_provider(VPLConfig(provider="flux")), FluxProvider)
    with pytest.raises(ProviderError):
        build_provider(VPLConfig(provider="nope"))


# --- caché -------------------------------------------------------------------

def test_cache_two_tier_key(tmp_path):
    cache = AssetCache(str(tmp_path))
    # reuse_key presente -> estable aunque cambie prompt/seed
    k1 = cache.key(_req(reuse_key="loc", prompt="p1", seed=1), "mock", "m")
    k2 = cache.key(_req(reuse_key="loc", prompt="p2", seed=9), "mock", "m")
    assert k1 == k2
    # sin reuse_key -> depende de prompt/seed
    assert cache.key(_req(prompt="a"), "mock", "m") != cache.key(_req(prompt="b"), "mock", "m")
    # el proveedor forma parte de la clave (no invalida assets de otros proveedores)
    assert cache.key(_req(reuse_key="loc"), "mock", "m") != cache.key(_req(reuse_key="loc"), "openai", "m")


def test_cache_put_get(tmp_path):
    cache = AssetCache(str(tmp_path))
    cache.put("k1", _FAKE_PNG, {"shot_id": "s1"})
    got = cache.get("k1")
    assert got is not None and got[0] == _FAKE_PNG and got[1]["shot_id"] == "s1"
    assert cache.get("missing") is None


# --- reintentos --------------------------------------------------------------

def test_retry_transient_then_success():
    provider = _Flaky(fail_times=2)
    result, attempts = run_with_retry(lambda: provider.generate(_req()), max_retries=3, base_delay=0, sleep=lambda s: None)
    assert attempts == 2 and result.provider == "flaky"


def test_retry_permanent_raises():
    with pytest.raises(ProviderError):
        run_with_retry(lambda: _Broken().generate(_req()), max_retries=3, base_delay=0, sleep=lambda s: None)


# --- concurrencia ------------------------------------------------------------

def test_worker_pool_preserves_order():
    out = WorkerPool(workers=4).map(lambda x: x * 2, [1, 2, 3, 4, 5])
    assert out == [2, 4, 6, 8, 10]


# --- orquestador end-to-end (mock) ------------------------------------------

def _orchestrator(tmp_path, provider, **cfg):
    config = VPLConfig(provider="mock", workers=cfg.get("workers", 3),
                       max_retries=cfg.get("max_retries", 2), cache_dir=str(tmp_path / "cache"))
    return VisualGenerationOrchestrator(config=config, provider=provider,
                                        cache=AssetCache(str(tmp_path / "cache")), sleep=lambda s: None)


def test_end_to_end_mock_produces_images_and_manifest(tmp_path):
    out = str(tmp_path / "doc")
    orch = _orchestrator(tmp_path, MockVisualProvider())
    requests = [_req(shot_id=f"s{i}", prompt=f"shot {i}", seed=i) for i in range(5)]

    manifest = orch.generate(requests, documentary_id="demo", output_dir=out)

    images = sorted(os.listdir(os.path.join(out, "images")))
    metas = sorted(os.listdir(os.path.join(out, "metadata")))
    assert images == [f"S0{i}.png" for i in range(1, 6)]
    assert len(metas) == 5
    assert os.path.exists(os.path.join(out, "manifest.json"))
    assert manifest.total == 5 and manifest.failures == 0 and manifest.cache_misses == 5
    # PNG real en disco
    with open(os.path.join(out, "images", "S01.png"), "rb") as f:
        assert f.read(4) == b"\x89PNG"
    # manifest serializable y con assets
    data = json.loads(json.dumps(manifest.to_dict()))
    assert len(data["assets"]) == 5 and data["provider"] == "mock"


def test_cache_reuse_across_runs(tmp_path):
    out = str(tmp_path / "doc")
    requests = [_req(shot_id=f"s{i}", prompt=f"shot {i}", seed=i) for i in range(4)]

    m1 = _orchestrator(tmp_path, MockVisualProvider()).generate(requests, documentary_id="d", output_dir=out)
    m2 = _orchestrator(tmp_path, MockVisualProvider()).generate(requests, documentary_id="d", output_dir=out)
    assert m1.cache_misses == 4 and m1.cache_hits == 0
    assert m2.cache_hits == 4 and m2.cache_misses == 0   # 2ª ejecución -> todo cacheado


def test_location_reuse_within_run(tmp_path):
    out = str(tmp_path / "doc")
    requests = [
        _req(shot_id="s1", prompt="corner wide", reuse_key="corner_x"),
        _req(shot_id="s2", prompt="corner detail", reuse_key="corner_x"),  # misma localización
        _req(shot_id="s3", prompt="unique", reuse_key=""),
    ]
    m = _orchestrator(tmp_path, MockVisualProvider(), workers=1).generate(requests, documentary_id="d", output_dir=out)
    assert m.cache_hits == 1 and m.cache_misses == 2


def test_failures_recorded_without_crashing(tmp_path):
    out = str(tmp_path / "doc")
    m = _orchestrator(tmp_path, _Broken()).generate([_req("s1"), _req("s2")], documentary_id="d", output_dir=out)
    assert m.failures == 2 and len(m.failed) == 2 and len(m.assets) == 0


def test_retry_via_orchestrator(tmp_path):
    out = str(tmp_path / "doc")
    provider = _Flaky(fail_times=1)
    m = _orchestrator(tmp_path, provider, max_retries=2).generate([_req("s1")], documentary_id="d", output_dir=out)
    assert m.failures == 0 and m.retries == 1 and provider.calls == 2


# --- Coquito: 26 imágenes ----------------------------------------------------

def test_coquito_generates_26_images(tmp_path):
    from app.cli.compile_coquito import build_requests
    requests = build_requests()
    assert len(requests) == 26

    out = str(tmp_path / "coquito")
    orch = VisualGenerationOrchestrator(
        config=VPLConfig(provider="mock", workers=4, cache_dir=str(tmp_path / "cache")),
        provider=MockVisualProvider(), cache=AssetCache(str(tmp_path / "cache")), sleep=lambda s: None,
    )
    manifest = orch.generate(requests, documentary_id="coquito", output_dir=out)

    images = [f for f in os.listdir(os.path.join(out, "images")) if f.endswith(".png")]
    assert len(images) == 26
    assert manifest.total == 26 and manifest.failures == 0
    assert manifest.cache_hits >= 4    # localizaciones recurrentes reutilizadas
