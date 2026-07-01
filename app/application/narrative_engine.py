"""NarrativeEngine — transforma Facts en Scenes mediante un LLM (Sprint B-06).

Transformador *stateless*: entra ``list[Fact]``, sale ``list[Scene]``. No
persiste nada. Usa un LLM a través del puerto ``LLMProvider`` (la implementación
concreta —Claude/OpenAI/Gemini— vive en infraestructura, AP-006).

Reglas de dominio que el motor hace cumplir aunque el modelo se desvíe:
- No se inventan hechos: todo ``fact_id`` de una escena debe existir entre los
  hechos de entrada; los identificadores desconocidos se descartan.
- Trazabilidad estricta hecho → escena: cada escena conserva sus ``fact_ids``.
"""

import json

from app.application.llm_provider import LLMProvider
from app.domain.fact import Fact
from app.domain.narrative.scene import Scene

# Prompt del modelo — estrategia de composición documental (Sprint B-07).
# El esquema JSON de salida NO cambia (id/title/narration/fact_ids).
NARRATIVE_PROMPT = """You are an expert documentary narrative director.

Your job is to turn a list of verified facts into a cohesive, well-paced
documentary script told as a sequence of scenes.

GROUNDING (NON-NEGOTIABLE):
- You MUST NOT invent, infer, or add any fact that is not in the provided list.
- You MUST ONLY use the provided facts. No external knowledge, no speculation.
- You MAY rephrase, reorder and connect facts for storytelling, but every claim
  must stay faithful to the facts as given.
- Every scene MUST reference one or more of the provided fact_ids, and ONLY those
  exact ids. Never reference an id that is not in the list.

SCENE COMPOSITION:
- Group SEVERAL related facts into each scene. Do not produce one-fact-per-scene.
- Choose the number of scenes that best fits the material (typically 4-8). Do not
  pad, repeat, or force a fixed count; let the content decide.
- Arrange the scenes as a clear narrative arc:
  1. Hook — open on the most compelling angle to draw the viewer in.
  2. Tension / Development — establish the situation and what is at stake.
  3. Explanation / Insight — connect the facts and reveal what they mean.
  4. Conclusion — close on a resonant, fact-grounded takeaway.
- Each scene should flow naturally into the next; avoid abrupt, disconnected jumps.

STYLE:
- Documentary tone (BBC / Netflix narrator).
- Clear, spoken-word narration written to be read aloud as continuous prose.
- Short, vivid sentences; calm authority with light emotional engagement.
- Never sensationalist; never list-like.

OUTPUT FORMAT:
Return ONLY valid JSON — no prose, no commentary, no code fences:
{
  "scenes": [
    {
      "id": "s1",
      "title": "...",
      "narration": "...",
      "fact_ids": ["f1", "f2"]
    }
  ]
}"""


class NarrativeEngine:
    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm

    def generate(self, facts: list[Fact]) -> list[Scene]:
        """Transforma hechos verificados en un guion de escenas trazables."""
        if not facts:
            return []

        user = self._build_user_message(facts)
        raw = self._llm.complete(NARRATIVE_PROMPT, user)
        data = self._parse(raw)

        valid_ids = {fact.id for fact in facts}
        scenes: list[Scene] = []
        for index, item in enumerate(data.get("scenes", [])):
            scene = self._to_scene(item, index, valid_ids)
            if scene is not None:
                scenes.append(scene)
        return scenes

    @staticmethod
    def _build_user_message(facts: list[Fact]) -> str:
        payload = [{"id": fact.id, "text": fact.text} for fact in facts]
        return (
            "Here are the verified facts as JSON. Use ONLY these, and reference "
            "their exact ids in fact_ids. Group related facts into coherent "
            "scenes and shape them into a documentary narrative arc.\n\n"
            + json.dumps(payload, ensure_ascii=False)
        )

    @staticmethod
    def _parse(raw: str) -> dict:
        text = raw.strip()
        # El modelo puede envolver el JSON en vallas de código; lo saneamos.
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text
            if text.endswith("```"):
                text = text[: -3]
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:]
        text = text.strip()
        # Si quedara prosa alrededor, recortamos al objeto JSON externo.
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"El LLM no devolvió JSON válido: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError("El JSON del LLM no es un objeto.")
        return data

    @staticmethod
    def _to_scene(item: dict, index: int, valid_ids: set[str]) -> Scene | None:
        if not isinstance(item, dict):
            return None
        # No inventar hechos: descartamos fact_ids que no existan en la entrada.
        fact_ids = [
            fid for fid in item.get("fact_ids", []) if fid in valid_ids
        ]
        if not fact_ids:
            return None  # toda escena debe ser trazable a >= 1 hecho real
        return Scene(
            id=str(item.get("id") or f"s{index + 1}"),
            title=str(item.get("title", "")).strip(),
            narration=str(item.get("narration", "")).strip(),
            fact_ids=fact_ids,
        )
