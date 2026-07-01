"""EmotionalNarrativeDirector — capa de narración emocional (Sprint C-13).

Reescribe SOLO el campo ``narration`` de cada escena para darle voz de documental
(Netflix/HBO), usando un LLM a través del puerto ``LLMProvider``. Si no hay LLM
(o falla), degrada con elegancia devolviendo la narración determinista de C-12
sin cambios: el pipeline siempre corre.

INTEGRIDAD (no negociable): ``scene_id``, ``title``, ``fact_ids`` y el ORDEN se
toman SIEMPRE de las escenas originales; el LLM solo puede aportar texto nuevo de
narración. Cualquier cambio del modelo a la estructura se ignora. No se inventan
hechos: el modelo reexpresa el contenido ya derivado de los hechos.
"""

import json

from app.application.llm_provider import LLMProvider
from app.domain.narrative.scene import Scene

SYSTEM_PROMPT = """You are an emotional documentary narrative director.

You receive documentary scenes whose narration is a factual, deterministic
baseline. Rewrite ONLY the narration of each scene so it sounds like a Netflix /
HBO documentary voiceover: spoken, cinematic, emotionally engaging, smooth flow,
tension and release, human pacing.

NON-NEGOTIABLE:
- Do NOT invent, add, infer or import any new fact or external knowledge.
- Do NOT change the meaning of the existing content; only re-express it.
- Do NOT change scene order, scene ids, titles or fact_ids.
- Do NOT produce bullet points, lists or data-like narration.
- Keep each narration grounded in the same content as its baseline narration.

TONE BY ROLE (use the provided "role"):
- hook: curiosity, tension, unanswered questions.
- development: explanation with engaging flow.
- conflict: emphasize stakes and importance.
- resolution: closure, reflection, meaning.
- final: emotional, reflective conclusion.

OUTPUT FORMAT:
Return ONLY valid JSON — no prose, no code fences:
{
  "scenes": [
    { "scene_id": "...", "narration": "..." }
  ]
}
Include every scene_id you received, with its rewritten narration only."""


def _role(position: int, total: int) -> str:
    if total <= 1:
        return "hook"
    if position == 0:
        return "hook"
    if position == total - 1:
        return "final"
    if position == total - 2:
        return "resolution"
    if position == total // 2:
        return "conflict"
    return "development"


class EmotionalNarrativeDirector:
    def __init__(self, llm: LLMProvider | None) -> None:
        self._llm = llm

    def direct(self, scenes: list[Scene]) -> list[Scene]:
        if not scenes or self._llm is None:
            return list(scenes)

        try:
            user = self._build_user(scenes)
            raw = self._llm.complete(SYSTEM_PROMPT, user)
            rewritten = self._parse(raw)
        except Exception:
            return list(scenes)  # degradación: narración determinista intacta

        out: list[Scene] = []
        for scene in scenes:
            candidate = rewritten.get(scene.id)
            narration = (
                candidate.strip()
                if isinstance(candidate, str) and candidate.strip()
                else scene.narration  # sin reescritura válida -> baseline
            )
            out.append(
                Scene(
                    id=scene.id,            # bloqueado
                    title=scene.title,      # bloqueado
                    narration=narration,    # único cambio permitido
                    fact_ids=list(scene.fact_ids),  # bloqueado
                )
            )
        return out

    @staticmethod
    def _build_user(scenes: list[Scene]) -> str:
        total = len(scenes)
        payload = [
            {
                "scene_id": scene.id,
                "title": scene.title,
                "role": _role(index, total),
                "narration": scene.narration,
                "fact_ids": list(scene.fact_ids),
            }
            for index, scene in enumerate(scenes)
        ]
        return (
            "Rewrite ONLY the narration of each scene below, keeping it faithful to "
            "the same content. Return the same scene_ids.\n\n"
            + json.dumps(payload, ensure_ascii=False)
        )

    @staticmethod
    def _parse(raw: str) -> dict[str, str]:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text
            if text.endswith("```"):
                text = text[:-3]
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:]
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
        data = json.loads(text)
        result: dict[str, str] = {}
        for item in data.get("scenes", []):
            if isinstance(item, dict) and item.get("scene_id") is not None:
                result[str(item["scene_id"])] = str(item.get("narration", ""))
        return result


def scenes_to_contract(scenes: list[Scene]) -> list[dict]:
    """Serializa a la estructura de salida C-13 (scene_id/title/narration/fact_ids)."""
    return [
        {
            "scene_id": scene.id,
            "title": scene.title,
            "narration": scene.narration,
            "fact_ids": list(scene.fact_ids),
        }
        for scene in scenes
    ]
