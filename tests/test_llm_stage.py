"""Tests de la etapa LLM (fallback sin clave + ruta LLM con cliente falso)."""

import json
import os

from app.application.narrative_engine import NARRATIVE_PROMPT
from app.cli.llm_narrative_stage import run_llm_narrative_stage
from app.domain.evidence import Evidence
from app.domain.fact import Fact


class FakeClient:
    """Imita AnthropicLLMClient: registra prompt y respuesta cruda."""

    def __init__(self, scenes_json: str) -> None:
        self._scenes_json = scenes_json
        self.last_system = None
        self.last_user = None
        self.last_response = None

    def complete(self, system: str, user: str) -> str:
        self.last_system = system
        self.last_user = user
        self.last_response = {"id": "msg_fake", "content": [{"type": "text", "text": self._scenes_json}]}
        return self._scenes_json


def _facts():
    return [
        Fact(id="f0", evidence_id="e0", text="hecho cero"),
        Fact(id="f1", evidence_id="e1", text="hecho uno"),
    ]


def _evidence():
    return [
        Evidence(id="e0", research_id="r1", source_id="s0", content="x"),
        Evidence(id="e1", research_id="r1", source_id="s1", content="y"),
    ]


def test_fallback_when_no_api_key(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    result = run_llm_narrative_stage(
        _facts(), _evidence(), str(tmp_path), llm_client=None, log=lambda m: None
    )

    assert result.used_llm is False
    assert result.reason == "no_api_key"
    # No se escribe ningún artefacto LLM en el fallback.
    assert not os.path.exists(os.path.join(tmp_path, "scenes.json"))
    assert not os.path.exists(os.path.join(tmp_path, "prompt.md"))


def test_llm_path_persists_artifacts_and_provenance(tmp_path):
    scenes_json = json.dumps({"scenes": [
        {"id": "s1", "title": "Hook", "narration": "Intro.", "fact_ids": ["f0", "f1"]},
    ]})
    client = FakeClient(scenes_json)

    result = run_llm_narrative_stage(
        _facts(), _evidence(), str(tmp_path), llm_client=client, log=lambda m: None
    )

    assert result.used_llm is True
    assert result.scene_count == 1
    # Los cuatro artefactos exigidos existen.
    for name in ("scenes.json", "narrative_llm.md", "prompt.md", "response.json"):
        assert os.path.exists(os.path.join(tmp_path, name)), name

    # Procedencia completa Scene -> Fact -> Evidence -> Source.
    with open(os.path.join(tmp_path, "scenes.json"), encoding="utf-8") as handle:
        data = json.load(handle)
    prov = data["scenes"][0]["provenance"]
    assert prov["fact_ids"] == ["f0", "f1"]
    assert prov["evidence_ids"] == ["e0", "e1"]
    assert prov["source_ids"] == ["s0", "s1"]

    # prompt.md contiene el system (prompt obligatorio) y response.json la cruda.
    with open(os.path.join(tmp_path, "prompt.md"), encoding="utf-8") as handle:
        assert NARRATIVE_PROMPT in handle.read()
    with open(os.path.join(tmp_path, "response.json"), encoding="utf-8") as handle:
        assert json.load(handle)["id"] == "msg_fake"


def test_llm_failure_falls_back_without_breaking(tmp_path):
    class Boom:
        def complete(self, system, user):
            raise RuntimeError("api down")

    result = run_llm_narrative_stage(
        _facts(), _evidence(), str(tmp_path), llm_client=Boom(), log=lambda m: None
    )

    assert result.used_llm is False
    assert result.reason == "llm_error"
