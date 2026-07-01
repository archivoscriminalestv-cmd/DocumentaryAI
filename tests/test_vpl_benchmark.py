"""Tests del modo benchmark + registro de capacidades (VPL-003)."""

import json
import os

from app.vpl import BenchmarkRunner, provider_capabilities
from app.vpl.benchmark import BenchmarkReport, build_report
from app.vpl.models import GeneratedAsset, ProviderCapabilities
from app.vpl.provider import ProviderError
from app.vsc.models import VisualGenerationRequest


def _req(shot_id="s1"):
    return VisualGenerationRequest(
        shot_id=shot_id, scene_id="sc", media_type="image", prompt="a reactor", negative_prompt="cartoon",
        global_style="g", scene_style="s", shot_style="sh", camera="FX6", lens="35mm",
        lighting="soft", composition="thirds", color="muted", environment="Almassora", subject="Coquito",
        provider_constraints={"width": 1280, "height": 720, "aspect_ratio": "16:9"},
        reuse_key="", seed=7, seed_strategy="per_scene", motion_hint="locked",
    )


class FakeProvider:
    def __init__(self, name, *, available=True, fail=False, cost=0.04):
        self.name = name
        self.model = f"{name}-model"
        self._available, self._fail, self._cost = available, fail, cost

    def is_available(self):
        return self._available

    def generate(self, request):
        if self._fail:
            raise ProviderError(f"{self.name} falló")
        return GeneratedAsset(
            shot_id=request.shot_id, scene_id=request.scene_id, provider=self.name, model=self.model,
            prompt=request.prompt, negative_prompt=request.negative_prompt, seed=request.seed,
            width=1280, height=720, cost=self._cost, image_bytes=b"\x89PNG" + self.name.encode(),
            metadata={"src": self.name},
        )


# --- benchmark ---------------------------------------------------------------

def test_benchmark_records_cost_time_model_metadata(tmp_path):
    providers = [FakeProvider("openai", cost=0.04), FakeProvider("imagen", cost=0.02)]
    report = BenchmarkRunner(providers).run(_req(), output_dir=str(tmp_path))

    assert isinstance(report, BenchmarkReport)
    assert report.successes == 2
    by = {r["provider"]: r for r in report.results}
    assert by["openai"]["model"] == "openai-model" and by["openai"]["cost"] == 0.04
    assert by["imagen"]["metadata"]["src"] == "imagen"
    assert by["openai"]["resolution"] == "1280x720"
    assert by["openai"]["image_hash"]                      # hash calculado
    assert "generation_time" in by["openai"]               # tiempo medido
    # imágenes + informe escritos en disco
    assert os.path.exists(tmp_path / "openai.png")
    assert os.path.exists(tmp_path / "imagen.png")
    assert os.path.exists(tmp_path / "benchmark.json")


def test_benchmark_marks_unavailable_provider(tmp_path):
    report = BenchmarkRunner([FakeProvider("openai", available=False)]).run(_req(), output_dir=str(tmp_path))
    r = report.results[0]
    assert r["success"] is False and r["available"] is False
    assert "no configurado" in r["error"]
    assert not os.path.exists(tmp_path / "openai.png")     # no se generó nada


def test_benchmark_records_failure_without_blocking(tmp_path):
    providers = [FakeProvider("openai", fail=True), FakeProvider("mock")]
    report = BenchmarkRunner(providers).run(_req(), output_dir=str(tmp_path))
    by = {r["provider"]: r for r in report.results}
    assert by["openai"]["success"] is False and by["openai"]["error"]
    assert by["mock"]["success"] is True                   # el fallo de uno no frena al resto


def test_benchmark_report_picks_cheapest_and_fastest(tmp_path):
    providers = [FakeProvider("openai", cost=0.10), FakeProvider("imagen", cost=0.01)]
    report = BenchmarkRunner(providers).run(_req(), output_dir=str(tmp_path))
    assert report.cheapest == "imagen"
    text = build_report(report)
    assert "Benchmark" in text and "Cheapest:  imagen" in text
    assert "Successes: 2/2" in text


def test_benchmark_json_roundtrip(tmp_path):
    BenchmarkRunner([FakeProvider("mock", cost=0.0)]).run(_req(), output_dir=str(tmp_path))
    data = json.loads((tmp_path / "benchmark.json").read_text(encoding="utf-8"))
    assert data["providers"] == ["mock"]
    assert data["results"][0]["provider"] == "mock"
    assert data["successes"] == 1


# --- registro de capacidades -------------------------------------------------

def test_capabilities_registry_covers_all_providers():
    caps = provider_capabilities()
    assert set(caps) == {"mock", "openai", "imagen", "flux", "huggingface", "replicate"}
    assert all(isinstance(c, ProviderCapabilities) for c in caps.values())


def test_capabilities_reflect_provider_traits():
    caps = provider_capabilities()
    assert caps["imagen"].native_negative_prompt is True       # Imagen: negative nativo
    assert caps["openai"].native_negative_prompt is False      # OpenAI: se funde como Avoid
    assert caps["flux"].async_polling is True                  # Flux: submit->poll
    assert caps["flux"].self_hostable is True
    assert caps["mock"].cost_per_image == 0.0
    assert caps["mock"].available is True
    assert caps["openai"].requires_api_key == "OPENAI_API_KEY"
