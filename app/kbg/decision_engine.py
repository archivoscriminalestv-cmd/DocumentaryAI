"""Decision Engine (KBG) — traduce patrones aprendidos en parámetros concretos.

Reglas deterministas, sin IA, sin estética subjetiva, sin inventar. Cada decisión deriva su
``value``/``confidence`` ÚNICAMENTE del conocimiento disponible; si no hay señal suficiente
(p.ej. el dominante es ``UNKNOWN``), la decisión queda ``UNKNOWN``.
"""

from app.kbg import UNKNOWN
from app.kbg.models import Decision, GenerationKnowledge

_UNKNOWN_DOMINANCE = 0.5   # si 'UNKNOWN' >= 50% del reparto, no hay señal suficiente


def _unknown(key: str, reason: str, sources=None) -> Decision:
    return Decision(key=key, value=UNKNOWN, origin=UNKNOWN, confidence=0.0,
                    knowledge_sources=list(sources or []), reason=reason)


def _dominant(dist: dict):
    fractions = (dist or {}).get("fractions", {})
    total = (dist or {}).get("total", 0)
    if not fractions:
        return UNKNOWN, 0.0, total
    ordered = sorted(fractions.items(), key=lambda kv: (-kv[1], kv[0]))
    best_key, best_frac = ordered[0]
    if best_key == UNKNOWN:
        non_unknown = [(k, v) for k, v in ordered if k != UNKNOWN]
        if not non_unknown or best_frac >= _UNKNOWN_DOMINANCE:
            return UNKNOWN, 0.0, total
        return non_unknown[0][0], non_unknown[0][1], total
    return best_key, best_frac, total


def _decision_from_dist(key, dist, source, origin) -> Decision:
    value, frac, total = _dominant(dist)
    if value == UNKNOWN:
        return _unknown(key, "señal insuficiente: 'UNKNOWN' domina el reparto del corpus",
                        [source] if source else [])
    return Decision(key=key, value=value, origin=origin, confidence=round(frac, 4),
                    knowledge_sources=[source] if source else [],
                    reason=f"{round(frac * 100)}% '{value}' en el corpus (n={total})")


def _secondaries_decision(key, dist, source, origin) -> Decision:
    fractions = (dist or {}).get("fractions", {})
    dominant, _f, _t = _dominant(dist)
    if dominant == UNKNOWN:
        return _unknown(key, "sin valores secundarios fiables", [source] if source else [])
    seconds = [(k, v) for k, v in sorted(fractions.items(), key=lambda kv: (-kv[1], kv[0]))
               if k not in (UNKNOWN, dominant) and v > 0]
    if not seconds:
        return _unknown(key, "no hay valores secundarios", [source] if source else [])
    return Decision(key=key, value=[k for k, _ in seconds],
                    origin=origin, confidence=round(sum(v for _, v in seconds), 4),
                    knowledge_sources=[source] if source else [],
                    reason="secundarios por frecuencia: "
                           + ", ".join(f"{k} ({round(v * 100)}%)" for k, v in seconds))


def _decision_from_summary(key, summ, source, origin, field="median", unit="s") -> Decision:
    if not summ or summ.get("count", 0) <= 0:
        return _unknown(key, "sin datos numéricos en el corpus", [source] if source else [])
    mean = summ.get("mean", 0.0) or 0.0
    value = round(summ.get(field, 0.0), 3)
    confidence = round(min(1.0, summ.get("median", 0.0) / mean), 4) if mean else 0.0
    return Decision(key=key, value=value, origin=origin, confidence=confidence,
                    knowledge_sources=[source] if source else [],
                    reason=f"{field} {value}{unit} sobre {summ['count']} muestras "
                           f"(mean {round(mean, 3)})")


def build(resolved, genre: str, ece_coverage: dict | None = None) -> GenerationKnowledge:
    sections: dict[str, list[Decision]] = {}

    # --- Storytelling --------------------------------------------------------
    pacing_dist, pacing_src = resolved.dist("editing", "pacing_tier", "pacing_tier")
    shot_len, slen_src = resolved.summary("editing", "shot_length")
    sections["storytelling"] = [
        _decision_from_dist("pacing", pacing_dist, pacing_src, "DKS:editing_patterns"),
        _decision_from_summary("average_shot_duration", shot_len, slen_src,
                               "DKS:editing_patterns", field="median"),
        _unknown("average_scene_duration", "el corpus no sintetiza duración de escena"),
        _unknown("structure", "no hay conocimiento de estructura narrativa"),
        _unknown("narrative_type", "no hay conocimiento de tipo narrativo"),
        _unknown("information_density", "no hay conocimiento de densidad informativa"),
        _unknown("transition_type", "no hay conocimiento de transiciones"),
    ]

    # --- Cinematografía ------------------------------------------------------
    ss_dist, ss_src = resolved.dist("cinematography", "shot_size", "shot_size")
    mv_dist, mv_src = resolved.dist("motion", "movement", "movement")
    ct_dist, ct_src = resolved.dist("lighting", "color_temperature", "color_temperature")
    li_dist, li_src = resolved.dist("lighting", "lighting", "lighting")
    comp_dist, comp_src = resolved.dist("cinematography", "composition", None)
    contrast, contrast_src = resolved.summary("lighting", "contrast")
    brightness, bright_src = resolved.summary("lighting", "brightness")
    sections["cinematography"] = [
        _decision_from_dist("dominant_shot_size", ss_dist, ss_src, "DKS:cinematography_patterns"),
        _secondaries_decision("secondary_shot_sizes", ss_dist, ss_src, "DKS:cinematography_patterns"),
        _decision_from_dist("dominant_movement", mv_dist, mv_src, "DKS:motion_patterns"),
        _decision_from_dist("color_temperature", ct_dist, ct_src, "DKS:lighting_patterns"),
        _decision_from_dist("lighting", li_dist, li_src, "DKS:lighting_patterns"),
        _decision_from_summary("contrast", contrast, contrast_src, "DKS:lighting_patterns",
                               field="mean", unit=""),
        _decision_from_summary("brightness", brightness, bright_src, "DKS:lighting_patterns",
                               field="mean", unit=""),
        _decision_from_dist("composition", comp_dist, comp_src, "DKS:cinematography_patterns"),
        _unknown("negative_space", "no hay conocimiento de espacio negativo"),
        _unknown("rule_of_thirds", "no hay conocimiento de regla de tercios"),
    ]

    # --- Edición -------------------------------------------------------------
    cpm, cpm_src = resolved.summary("editing", "cuts_per_minute")
    cadence = _decision_from_dist("cadence", pacing_dist, pacing_src, "DKS:editing_patterns")
    cadence.key = "cadence"
    sections["editing"] = [
        _unknown("cut_type", "no hay conocimiento de tipo de corte"),
        _decision_from_summary("cuts_per_minute", cpm, cpm_src, "DKS:editing_patterns",
                               field="mean", unit="/min"),
        cadence,
        _unknown("broll_frequency", "requiere ECE/uso real (no disponible)"),
        _unknown("use_of_maps", "requiere ECE (cobertura) del caso"),
        _unknown("use_of_documents", "requiere ECE (cobertura) del caso"),
        _unknown("use_of_recreations", "requiere ECE (recreation_candidates) del caso"),
    ]

    # --- Narración / Música (sin conocimiento sintetizado todavía) -----------
    sections["narration"] = [_unknown(k, "no hay conocimiento de narración sintetizado")
                             for k in ("type", "rhythm", "pauses", "density", "style")]
    sections["music"] = [_unknown(k, "no hay conocimiento de música sintetizado")
                         for k in ("intensity", "energy", "evolution", "changes")]

    # --- Evidencias (mezcla real desde el ECE del caso, si está disponible) --
    sections["evidence"] = _evidence_decisions(ece_coverage)

    summary = _summarize(sections)
    return GenerationKnowledge(genre=genre, sections=sections, summary=summary)


def _evidence_decisions(ece_coverage: dict | None) -> list[Decision]:
    types = ("photographs", "videos", "documents", "maps", "news")
    if not isinstance(ece_coverage, dict):
        base = [_unknown(t, "requiere coverage_report del ECE del caso") for t in types]
        base += [_unknown(k, "requiere ECE/recreation_candidates del caso")
                 for k in ("material_real", "recreations", "animations")]
        return base

    dims = {d.get("name"): d for d in ece_coverage.get("dimensions", [])}
    total = sum(int(dims.get(t, {}).get("discovered", 0)) for t in types)
    out: list[Decision] = []
    for t in types:
        discovered = int(dims.get(t, {}).get("discovered", 0))
        if total <= 0:
            out.append(_unknown(t, "sin evidencia descubierta en el ECE", ["ece:coverage_report"]))
            continue
        frac = round(discovered / total, 4)
        out.append(Decision(key=t, value=frac, origin="ECE:coverage_report",
                            confidence=frac, knowledge_sources=["ece:coverage_report"],
                            reason=f"{discovered}/{total} evidencias reales son '{t}'"))
    # real vs recreaciones/animaciones no se infiere aquí (sin datos suficientes)
    out += [_unknown(k, "no inferible solo desde coverage_report")
            for k in ("material_real", "recreations", "animations")]
    return out


def _summarize(sections: dict[str, list[Decision]]) -> dict:
    known = sum(1 for ds in sections.values() for d in ds if d.known)
    total = sum(len(ds) for ds in sections.values())
    return {
        "total_decisions": total, "known": known, "unknown": total - known,
        "known_ratio": round(known / total, 4) if total else 0.0,
        "by_section": {name: {"known": sum(1 for d in ds if d.known), "total": len(ds)}
                       for name, ds in sections.items()},
    }
