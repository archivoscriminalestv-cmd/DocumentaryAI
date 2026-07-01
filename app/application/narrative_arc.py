"""NarrativeArcBuilder — estructura de arco documental (Sprint C-12, fix de calidad).

Convierte los hechos verificados en una secuencia con ARCO narrativo
(hook → contexto → desarrollo → punto clave → consecuencias → cierre), agrupando
varios hechos por escena para evitar el efecto "PowerPoint" (un hecho por slide).

Reglas (C-12):
- Escena 1 = INTRO DE CANAL (sin fact_ids; no es lógica narrativa).
- Escenas 2..N = narrativa, cada una con ≥1 ``fact_id``.
- Nunca menos de 4 escenas narrativas (→ ≥5 escenas totales con la intro).
- INTEGRIDAD DE HECHOS: solo se agrupan/reordenan/conectan los hechos provistos;
  jamás se inventan datos nuevos. La "voz documental" se logra con conectores
  estructurales (no factuales), no añadiendo información.
"""

from app.domain.narrative.scene import Scene

# Roles del arco, en orden. (id, título de escena, conector estructural no factual)
_ROLES: list[tuple[str, str, str]] = [
    ("hook", "El punto de partida", "Hay un punto de partida que merece atención."),
    ("context", "El contexto", "Para entender lo ocurrido, conviene situar los hechos en su contexto."),
    ("development", "El desarrollo de los hechos", "A partir de ahí, los hechos se encadenan."),
    ("conflict", "La cuestión clave", "En el centro de esta historia hay una cuestión clave."),
    ("consequences", "Las consecuencias", "Estos hechos no quedaron sin consecuencias."),
    ("closing", "Lo que sostienen las evidencias", "Esto es lo que las evidencias permiten afirmar."),
]

_MIN_NARRATIVE_SCENES = 4
_MAX_NARRATIVE_SCENES = len(_ROLES)  # 6

_INTRO_SCENE = {
    "scene_id": "scene-01-intro",
    "title": "Channel Intro",
    "narration": "",
    "fact_ids": [],
}


def _clean(text: str) -> str:
    cleaned = " ".join(str(text or "").split())
    if cleaned and cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned


class NarrativeArcBuilder:
    def build(self, facts: list) -> list[dict]:
        """Contrato de salida C-12: [intro, narrativa...] como dicts JSON."""
        scenes: list[dict] = [dict(_INTRO_SCENE)]
        for index, (title, narration, fact_ids) in enumerate(self._arc(facts), start=2):
            scenes.append(
                {
                    "scene_id": f"scene-{index:02d}",
                    "title": title,
                    "narration": narration,
                    "fact_ids": fact_ids,
                }
            )
        return scenes

    def narrative_scenes(self, facts: list) -> list[Scene]:
        """Escenas narrativas (sin la intro) para el pipeline existente.

        La intro de canal la inyecta aguas abajo MediaStyleService/FinalRender en
        la primera escena, así que aquí se devuelven solo las escenas de contenido.
        """
        return [
            Scene(id=f"scene-{index:02d}", title=title, narration=narration, fact_ids=fact_ids)
            for index, (title, narration, fact_ids) in enumerate(self._arc(facts), start=2)
        ]

    def _arc(self, facts: list) -> list[tuple[str, str, list[str]]]:
        """Reparte los hechos en etapas de arco. Devuelve (title, narration, fact_ids)."""
        if not facts:
            return []

        stage_count = min(_MAX_NARRATIVE_SCENES, max(_MIN_NARRATIVE_SCENES, len(facts)))
        groups = self._distribute(facts, stage_count)

        stages: list[tuple[str, str, list[str]]] = []
        for position, group in enumerate(groups):
            _, title, connector = _ROLES[position]
            stages.append((title, self._narration(connector, group), self._fact_ids(group)))
        return stages

    @staticmethod
    def _distribute(facts: list, stage_count: int) -> list[list]:
        """Agrupa los hechos en ``stage_count`` grupos contiguos.

        Si hay menos hechos que etapas, se reutiliza un hecho por etapa (solo
        reorganización: nunca se inventan hechos) para que ninguna escena
        narrativa quede sin ``fact_ids``.
        """
        if len(facts) >= stage_count:
            # Partición contigua equilibrada en EXACTAMENTE stage_count grupos,
            # sin repetir ni omitir hechos (las primeras etapas reciben uno más).
            base, extra = divmod(len(facts), stage_count)
            groups: list[list] = []
            cursor = 0
            for i in range(stage_count):
                take = base + (1 if i < extra else 0)
                groups.append(facts[cursor : cursor + take])
                cursor += take
            return groups
        # Menos hechos que etapas: una etapa por hecho y se rellena reutilizando.
        return [[facts[i % len(facts)]] for i in range(stage_count)]

    @staticmethod
    def _narration(connector: str, group: list) -> str:
        body = " ".join(
            _clean(getattr(fact, "text", ""))
            for fact in group
            if str(getattr(fact, "text", "")).strip()
        )
        # Conector estructural (no factual) + hechos verbatim → prosa, no lista.
        return f"{connector} {body}".strip() if body else connector

    @staticmethod
    def _fact_ids(group: list) -> list[str]:
        seen: list[str] = []
        for fact in group:
            fid = str(getattr(fact, "id", ""))
            if fid and fid not in seen:
                seen.append(fid)
        return seen
