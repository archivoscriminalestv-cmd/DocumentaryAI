"""Tests del preflight de credenciales + informes de render (telemetry/report)."""

import pytest

from app.vpl.models import GenerationManifest
from app.vpl.preflight import (
    INVALID,
    NOT_CONFIGURED,
    OK,
    check_provider,
    format_report,
    run_preflight,
    valid_providers,
)
from app.vpl.provider import ProviderError
from app.vpl.telemetry import build_render_report, build_telemetry


def _ok_get(url, headers, timeout):
    return {"data": []}


def _auth_fail_get(url, headers, timeout):
    raise ProviderError("HTTP 401: invalid key", transient=False)


def _net_fail_get(url, headers, timeout):
    raise ProviderError("network error", transient=True)


# --- preflight por proveedor -------------------------------------------------

def test_check_provider_not_configured(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    r = check_provider("openai", "OpenAI", "OPENAI_API_KEY", http_get=_ok_get)
    assert r.status == NOT_CONFIGURED and r.valid is False


def test_check_provider_valid(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    r = check_provider("openai", "OpenAI", "OPENAI_API_KEY", http_get=_ok_get)
    assert r.status == OK and r.valid is True


def test_check_provider_invalid_key(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "bad")
    r = check_provider("imagen", "Google Imagen", "GOOGLE_API_KEY", http_get=_auth_fail_get)
    assert r.status == INVALID and r.valid is False


def test_check_provider_transient_is_not_invalid(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    r = check_provider("openai", "OpenAI", "OPENAI_API_KEY", http_get=_net_fail_get)
    assert r.valid is False and r.status != INVALID    # error recuperable, no clave inválida


def test_run_preflight_and_valid_providers(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setenv("GOOGLE_API_KEY", "bad")
    monkeypatch.setenv("HF_TOKEN", "hf")
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)

    def routed_get(url, headers, timeout):
        if "openai.com" in url:
            return {"data": []}
        if "huggingface.co" in url:
            return {"name": "tester"}
        raise ProviderError("HTTP 400: bad", transient=False)

    results = run_preflight(http_get=routed_get)
    by = {r.name: r for r in results}
    assert by["openai"].status == OK
    assert by["imagen"].status == INVALID
    assert by["huggingface"].status == OK
    assert by["replicate"].status == NOT_CONFIGURED
    assert valid_providers(results) == ["openai", "huggingface"]


def test_format_report_layout(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    results = run_preflight(http_get=_ok_get)
    text = format_report(results)
    assert "OpenAI" in text and " OK" in text
    assert "Replicate" in text and NOT_CONFIGURED in text
    # alineación con puntos
    assert "." in text.splitlines()[0]


# --- informes de render ------------------------------------------------------

def _manifest():
    return GenerationManifest(
        documentary_id="coquito", provider="openai>mock", model="gpt-image-1",
        timestamp="2026-06-29T00:00:00Z", duration_seconds=42.0, total=2,
        cache_hits=1, cache_misses=1, failures=0, retries=0,
        assets=[
            {"shot_id": "s1", "scene": "scene-01", "provider": "openai", "model": "gpt-image-1",
             "generation_time": 3.0, "cost": 0.04, "resolution": "1280x720",
             "image_hash": "abc123", "status": "generated", "filename": "S01.png",
             "metadata": {"chain_winner": "openai"}},
            {"shot_id": "s2", "scene": "scene-01", "provider": "mock", "model": "mock-1",
             "generation_time": 0.0, "cost": 0.0, "resolution": "1280x720",
             "image_hash": "def456", "status": "cached", "filename": "S02.png",
             "metadata": {"chain_winner": "mock"}},
        ],
        failed=[],
    )


def test_build_telemetry_structure():
    t = build_telemetry(_manifest())
    assert t["images"] == 2 and t["cache_hits"] == 1
    assert t["total_cost"] == 0.04
    assert t["provider_breakdown"] == {"openai": 1, "mock": 1}
    assert t["shots"][0]["provider"] == "openai" and t["shots"][0]["hash"] == "abc123"


def test_build_render_report_markdown():
    md = build_render_report(_manifest())
    assert "# Render report — coquito" in md
    assert "Total cost:** $0.0400" in md
    assert "| S01.png |" in md and "openai" in md
    assert "Provider breakdown:** openai: 1, mock: 1" in md
