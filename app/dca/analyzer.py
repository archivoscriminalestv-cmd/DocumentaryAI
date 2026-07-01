"""Analyzer (DCA) — responde, mediante reglas objetivas, qué hay y qué falta.

Sin IA, sin scoring subjetivo, sin inferencias. Detecta: capacidades requeridas que nadie
produce, motores no integrados, capacidades duplicadas, motores sin consumidores y
conocimiento que el pipeline aún no aprovecha. Determinista.
"""

from app.dca.models import Bottleneck, Gap, Status, Subsystem

# Capacidades de "conocimiento" cuya falta de consumo en generación es relevante.
_KNOWLEDGE_CAPS = {"cinematographic_knowledge", "style_patterns", "youtube_intelligence",
                   "visual_attributes", "cinematic_profile", "production_gaps"}
_GENERATION_DOMAINS = {"visual_generation", "assembly", "motion"}


def _producers(subsystems, cap):
    return sorted(s.name for s in subsystems if cap in s.produces)


def _consumers(subsystems, cap):
    return sorted(s.name for s in subsystems if cap in s.consumes)


def detect_gaps(subsystems: list[Subsystem]) -> list[Gap]:
    gaps: list[Gap] = []
    all_produced = {c for s in subsystems for c in s.produces}
    all_consumed = {c for s in subsystems for c in s.consumes}

    # 1) capacidades consumidas que nadie produce
    for cap in sorted(all_consumed - all_produced):
        gaps.append(Gap(id=f"gap:missing:{cap}", kind="missing_capability",
                        description=f"La capacidad '{cap}' la consumen "
                                    f"{_consumers(subsystems, cap)} pero no la produce nadie.",
                        related=_consumers(subsystems, cap)))

    # 2) capacidades duplicadas (más de un productor)
    for cap in sorted(all_produced):
        producers = _producers(subsystems, cap)
        if len(producers) > 1:
            gaps.append(Gap(id=f"gap:duplicate:{cap}", kind="duplicate",
                            description=f"'{cap}' la producen varios motores: {producers}.",
                            related=producers))

    # 3) motores no integrados
    for s in subsystems:
        if s.status == Status.NOT_INTEGRATED:
            gaps.append(Gap(id=f"gap:not_integrated:{s.name}", kind="not_integrated",
                            description=f"{s.name} está implementado pero no integrado en el pipeline.",
                            related=[s.name]))

    # 4) motores sin consumidores (sus capacidades no las consume nadie) y no terminales
    for s in subsystems:
        if not s.produces:
            continue
        if all(not _consumers(subsystems, c) for c in s.produces) and s.domain != "assembly":
            gaps.append(Gap(id=f"gap:unused:{s.name}", kind="unused",
                            description=f"Nadie consume las salidas de {s.name} ({s.produces}).",
                            related=[s.name]))

    # 5) conocimiento no aprovechado por la generación
    gen = [s for s in subsystems if s.domain in _GENERATION_DOMAINS]
    gen_consumes = {c for s in gen for c in s.consumes}
    for cap in sorted(_KNOWLEDGE_CAPS & all_produced):
        if cap not in gen_consumes:
            gaps.append(Gap(id=f"gap:knowledge_unused:{cap}", kind="knowledge_unused",
                            description=f"El conocimiento '{cap}' aún no lo aprovecha la generación.",
                            related=_producers(subsystems, cap)))

    gaps.sort(key=lambda g: g.id)
    return gaps


def detect_bottlenecks(subsystems: list[Subsystem]) -> list[Bottleneck]:
    bottlenecks: list[Bottleneck] = []
    for s in subsystems:
        consumers = sorted({c.name for c in subsystems
                            for cap in s.produces if cap in c.consumes})
        # un cuello de botella objetivo: produce algo que consumen >=1, pero no está integrado
        if s.status in (Status.NOT_INTEGRATED, Status.DESIGN, Status.PLANNED) and consumers:
            bottlenecks.append(Bottleneck(
                id=f"bottleneck:{s.name}", subsystem=s.name,
                reason=f"{s.name} ({s.status}) bloquea a {len(consumers)} consumidor(es).",
                consumers=len(consumers)))
    bottlenecks.sort(key=lambda b: (-b.consumers, b.subsystem))
    return bottlenecks


def consumers_count(subsystems: list[Subsystem], name: str) -> int:
    target = next((s for s in subsystems if s.name == name), None)
    if target is None:
        return 0
    return len({c.name for c in subsystems for cap in target.produces if cap in c.consumes})
