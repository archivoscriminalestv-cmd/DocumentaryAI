"""Tests de los adaptadores reales del AIM (AIM-002) — deterministas, HTTP mockeado."""

from app.aim.errors import ErrorClass
from app.aim.http import MappingHttpClient, SequenceHttpClient
from app.aim.models import Capability as C
from app.aim.models import HealthState
from app.aim.orchestrator import APIIntegrationManager
from app.aim.registry import default_registry
from app.aim.retry import CircuitBreaker
from app.aim.secrets import SecretManager


def _mgr(*, env=None, routes=None, status_routes=None, seq=None, breaker=None):
    secrets = SecretManager(env=env or {})
    http = (SequenceHttpClient(seq) if seq is not None
            else MappingHttpClient(routes or [], status_routes or []))
    reg = default_registry(secrets, http=http, breaker=breaker, sleep=lambda _s: None)
    return APIIntegrationManager(secrets=secrets, registry=reg), http


# --- contrato / autenticación ------------------------------------------------
def test_adapter_contract_methods():
    mgr, _ = _mgr(env={"OPENAI_API_KEY": "x"})
    openai = mgr.registry.get("openai")
    assert openai.provider_name() == "openai" and openai.version()
    assert C.LLM in openai.capabilities() and openai.cost() == "paid"
    assert openai.authenticate() == {"required": True, "configured": True, "status": "yes"}


def test_authenticate_states():
    mgr_no, _ = _mgr(env={})
    assert mgr_no.registry.get("openai").authenticate()["status"] == "no"
    assert mgr_no.registry.get("wikipedia").authenticate()["status"] == "not_required"


# --- execute real (HTTP mockeado) --------------------------------------------
def test_wikipedia_search_execute():
    mgr, _ = _mgr(routes=[("wikipedia.org", {"query": {"search": [
        {"title": "Zodiac Killer", "pageid": 34176}]}})])
    r = mgr.registry.get("wikipedia").execute("search", query="zodiac")
    assert r.ok and r.value[0]["title"] == "Zodiac Killer"


def test_openai_complete_execute():
    mgr, _ = _mgr(env={"OPENAI_API_KEY": "x"},
                  routes=[("chat/completions", {"choices": [{"message": {"content": "hello"}}]})])
    r = mgr.execute(C.LLM, "complete", system="s", user="u")   # anthropic(primary, contrato)→openai
    assert r.ok and r.value == "hello" and r.provider == "openai"


def test_execute_without_credentials_is_unavailable_unknown():
    mgr, _ = _mgr(env={})
    r = mgr.registry.get("openai").execute("complete", user="u")
    assert r.status == "unavailable" and r.value == "UNKNOWN" and r.error_class == ErrorClass.AUTH


# --- selección de proveedor / fallback ---------------------------------------
def test_provider_selection_fallback_to_alternative():
    # sin OpenAI key; con Replicate key -> AIM cae al alternativo que SÍ puede ejecutar
    mgr, _ = _mgr(env={"REPLICATE_API_TOKEN": "x"},
                  routes=[("replicate.com", {"id": "pred1", "status": "starting"})])
    r = mgr.execute(C.IMAGE, "generate_image", prompt="a cat")
    assert r.ok and r.provider == "replicate" and r.value["prediction_id"] == "pred1"


def test_resolution_unknown_when_no_provider_usable():
    mgr, _ = _mgr(env={})                              # ninguna credencial
    r = mgr.execute(C.IMAGE, "generate_image", prompt="x")
    assert not r.ok and r.value == "UNKNOWN"


# --- retry / rate limit / timeout / circuit breaker --------------------------
def test_retry_then_success():
    mgr, http = _mgr(seq=[503, 503, {"query": {"search": [{"title": "T", "pageid": 1}]}}])
    r = mgr.registry.get("wikipedia").execute("search", query="x")
    assert r.ok and r.retries == 2 and http.calls == 3


def test_retry_exhausted_rate_limit():
    mgr, _ = _mgr(seq=[429, 429, 429])
    r = mgr.registry.get("wikipedia").execute("search", query="x")
    assert r.status == "error" and r.error_class == ErrorClass.RATE_LIMIT and r.retries == 2


def test_timeout_classified():
    mgr, _ = _mgr(seq=[TimeoutError("slow")])
    r = mgr.registry.get("wikipedia").execute("search", query="x")
    assert r.status == "error" and r.error_class == ErrorClass.TIMEOUT


def test_invalid_response_classified():
    mgr, _ = _mgr(status_routes=[("wikipedia.org", 400)])
    r = mgr.registry.get("wikipedia").execute("search", query="x")
    assert r.status == "error" and r.error_class == ErrorClass.INVALID_RESPONSE


def test_circuit_breaker_opens_after_failures():
    mgr, _ = _mgr(status_routes=[("wikipedia.org", 500)], breaker=CircuitBreaker(threshold=1))
    wiki = mgr.registry.get("wikipedia")
    first = wiki.execute("search", query="x")
    second = wiki.execute("search", query="x")
    assert first.status == "error"
    assert second.status == "unavailable" and second.note == "circuit_open"


# --- health real -------------------------------------------------------------
def test_health_probe_ready_and_auth_failed():
    ok, _ = _mgr(env={"OPENAI_API_KEY": "x"}, routes=[("api.openai.com", {"data": []})])
    assert ok.registry.get("openai").health(probe=True).state == HealthState.READY
    bad, _ = _mgr(env={"OPENAI_API_KEY": "x"}, status_routes=[("api.openai.com", 401)])
    assert bad.registry.get("openai").health(probe=True).state == HealthState.AUTH_FAILED


# --- métricas (sin datos sensibles) ------------------------------------------
def test_metrics_recorded_without_sensitive_data():
    mgr, _ = _mgr(routes=[("wikipedia.org", {"query": {"search": []}})])
    mgr.registry.get("wikipedia").execute("search", query="secret-prompt")
    metrics = mgr.metrics()
    assert metrics and metrics[0]["provider"] == "wikipedia" and metrics[0]["operation"] == "search"
    for m in metrics:
        assert "prompt" not in m and "query" not in m and "api_key" not in m
    assert mgr.metrics_summary()["total_calls"] >= 1


# --- capability matrix con estado --------------------------------------------
def test_capability_matrix_has_primary_and_status():
    mgr, _ = _mgr(env={"OPENAI_API_KEY": "x"})
    matrix = mgr.capability_matrix()
    img = matrix["by_capability"][C.IMAGE]
    assert img["primary"] == "openai" and img["status"] == HealthState.CONFIGURED
    assert "replicate" in img["providers"]
