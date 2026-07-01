"""Tests del API Integration Manager (AIM-001) — deterministas, sin red, sin credenciales reales."""

import json
import os

from app.aim.capability_matrix import build_capability_matrix
from app.aim.health import check_all
from app.aim.models import Capability as C
from app.aim.models import Category, HealthState
from app.aim.orchestrator import APIIntegrationManager
from app.aim.persistence import write_outputs
from app.aim.registry import default_registry
from app.aim.secrets import SecretManager


def _mgr(env=None, root="."):
    secrets = SecretManager(env=env if env is not None else {})
    return APIIntegrationManager(secrets=secrets, registry=default_registry(secrets), root=root)


# --- secret manager ----------------------------------------------------------
def test_secret_manager_sources_and_masking(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DEEPL_API_KEY=abc\n# comment\nFOO=bar\n", encoding="utf-8")
    sm = SecretManager(env={"OPENAI_API_KEY": "x"}, dotenv_path=str(env_file))
    assert sm.has("OPENAI_API_KEY") and sm.get("OPENAI_API_KEY") == "x"
    assert sm.get("DEEPL_API_KEY") == "abc"          # del .env
    assert sm.has("NOPE") is False
    assert sm.mask("OPENAI_API_KEY", "x") == "configured"   # nunca el valor
    assert sm.mask("NOPE", None) == "missing"


# --- registry / resolución ---------------------------------------------------
def test_registry_by_capability_and_resolution():
    mgr = _mgr()
    image = mgr.resolve(C.IMAGE)
    assert "openai" in image and "stability" in image
    # ordenado por prioridad (openai prio 10 antes que stability 20)
    assert image.index("openai") < image.index("stability")
    assert mgr.primary(C.LLM) == "anthropic"          # prio 5 < openai 10
    assert mgr.registry.by_category(Category.EVIDENCE)


def test_capability_matrix():
    matrix = build_capability_matrix(_mgr().registry)
    assert "openai" in matrix["by_capability"][C.LLM]["providers"]
    assert matrix["by_capability"][C.LLM]["primary"] == "anthropic"
    assert C.IMAGE in matrix["by_provider"]["openai"]


# --- health ------------------------------------------------------------------
def test_health_no_credentials():
    mgr = _mgr(env={})                                # sin claves
    h = {x.provider: x for x in mgr.health_report()}
    assert h["europeana"].state == HealthState.NO_CREDENTIALS and h["europeana"].authenticated == "no"
    assert h["openai"].state == HealthState.NO_CREDENTIALS
    # proveedor público con adaptador y sin clave -> configurado (sin probe)
    assert h["wikipedia"].state == HealthState.CONFIGURED and h["wikipedia"].authenticated == "not_required"


def test_health_with_credentials_is_configured():
    mgr = _mgr(env={"OPENAI_API_KEY": "x"})
    h = {x.provider: x for x in mgr.health_report()}
    # con clave + adaptador real -> configurado (no no_credentials)
    assert h["openai"].state == HealthState.CONFIGURED and h["openai"].authenticated == "yes"


def test_health_probe_measures_connectivity():
    from app.aim.http import MappingHttpClient
    from app.aim.registry import default_registry
    secrets = SecretManager(env={})
    http = MappingHttpClient([("wikipedia.org", {"query": {"search": []}})])
    mgr = APIIntegrationManager(secrets=secrets, registry=default_registry(secrets, http=http))
    statuses = {x.provider: x for x in mgr.health_report(probe=True)}
    wiki = statuses["wikipedia"]
    assert wiki.state == HealthState.READY and wiki.reachable == "yes" and wiki.latency_ms is not None


def test_health_check_all_is_deterministic():
    reg = _mgr().registry
    assert [s.to_dict() for s in check_all(reg)] == [s.to_dict() for s in check_all(reg)]


# --- readiness ---------------------------------------------------------------
def test_readiness_report(tmp_path):
    mgr = _mgr(env={"OPENAI_API_KEY": "x"}, root=str(tmp_path))
    report = mgr.readiness()
    items = {i.name: i for i in report.items}
    assert items["wikipedia"].ready is True           # público
    assert items["europeana"].ready is False and items["europeana"].state == HealthState.NO_CREDENTIALS
    assert items["yt-dlp"].category == Category.LEARNING
    assert items["knowledge"].category == Category.KNOWLEDGE
    s = report.summary
    assert s["total"] == len(report.items) and 0 < s["ready"] < s["total"]
    assert "by_category" in s


def test_readiness_is_deterministic(tmp_path):
    a = _mgr(env={}, root=str(tmp_path)).readiness().to_dict()
    b = _mgr(env={}, root=str(tmp_path)).readiness().to_dict()
    assert a == b


# --- persistencia ------------------------------------------------------------
def test_persistence_writes_four_files(tmp_path):
    mgr = _mgr(env={"OPENAI_API_KEY": "supersecret"}, root=str(tmp_path))
    paths = write_outputs(str(tmp_path / "system"), mgr)
    for name in ("production_readiness.json", "provider_status.json",
                 "provider_capabilities.json", "provider_metrics.json"):
        assert os.path.exists(paths[name])
    # NUNCA se persiste el valor de una credencial en ningún fichero
    for path in paths.values():
        assert "supersecret" not in open(path, encoding="utf-8").read()
    status = json.load(open(paths["provider_status.json"], encoding="utf-8"))["providers"]
    assert any(p["name"] == "openai" and p["state"] == HealthState.CONFIGURED for p in status)
