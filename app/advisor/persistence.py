"""Persistencia del Advisor: escribe los informes FUERA de knowledge/.

Por defecto en ``output/advisor/`` para no interferir nunca con la base de conocimiento
(que puede estar siendo escrita por un proceso de aprendizaje). Reproducible.
"""

import json
import os

from app.advisor.models import AdvisorReport


class ReportWriter:
    """Implementación por defecto de ``ReportSink`` (escribe en output/advisor/)."""

    def __init__(self, out_dir: str = os.path.join("output", "advisor")) -> None:
        self.out_dir = out_dir

    def _w(self, name: str, payload) -> str:
        path = os.path.join(self.out_dir, name)
        with open(path, "w", encoding="utf-8") as h:
            if isinstance(payload, str):
                h.write(payload)
            else:
                json.dump(payload, h, ensure_ascii=False, indent=2, sort_keys=True)
        return path

    def write(self, report: AdvisorReport) -> dict[str, str]:
        os.makedirs(self.out_dir, exist_ok=True)
        paths = {
            # ADV-001 (compat)
            "json": self._w("advisor_report.json", report.to_dict()),
            "markdown": self._w("advisor_report.md", render_report(report)),
            # ADV-002 (informe nuevo)
            "production_advisor": self._w("production_advisor.md", render_production_advisor(report)),
            "capability_matrix": self._w(
                "capability_matrix.json", {"rows": [r.to_dict() for r in report.capability_matrix]}),
            "gap_report": self._w("gap_report.json", {
                "gaps": [g.to_dict() for g in report.gaps],
                "completeness": [c.to_dict() for c in report.completeness],
                "confidence_notes": list(report.confidence_notes),
            }),
            "discoveries": self._w(
                "discoveries.json", {"discoveries": [d.to_dict() for d in report.discoveries]}),
        }
        return paths


def render_report(report: AdvisorReport) -> str:
    s = report.snapshot
    lines = [
        "# Production Advisor report (scaffold)",
        "",
        f"- **Schema:** {report.schema_version}  ·  **From:** `{report.generated_from}`",
        f"- **Corpus available:** {'yes' if s.available else 'no'}",
        f"- **Documentaries:** {s.documentaries}  ·  **Hours:** {s.hours:.2f}  ·  "
        f"**Shots:** {s.shots}  ·  **Scenes:** {s.scenes}",
        f"- **Sources read:** {', '.join(s.sources_read) or '—'}",
        "",
        "## Capability coverage (corpus % pending public signal)",
        "",
        "| Capability | Corpus % | Pipeline |",
        "|------------|---------:|----------|",
        *[f"| {c.capability} | {'—' if c.corpus_percent is None else f'{c.corpus_percent:.0%}'} "
          f"| {c.pipeline_supported} |" for c in s.capabilities],
        "",
        "## Gaps",
        "",
        *([f"- **[{g.severity}] {g.title}** ({g.dimension}) — {g.rationale}" for g in report.gaps]
          or ["- (none)"]),
        "",
        "## Recommendations (priority desc)",
        "",
        *([f"- **{r.title}** · impact {r.impact} / effort {r.effort} · prio {r.priority} — {r.rationale}"
           for r in report.recommendations] or ["- (none)"]),
        "",
        "## Notes",
        "",
        *([f"- {n}" for n in report.notes] or ["- (none)"]),
        "",
    ]
    return "\n".join(lines)


def render_production_advisor(report: AdvisorReport) -> str:
    """Informe principal ADV-002 (production_advisor.md)."""
    s = report.snapshot
    lines = [
        "# Production Advisor — Corpus vs Pipeline",
        "",
        f"- **From:** `{report.generated_from}`  ·  **Corpus available:** "
        f"{'yes' if s.available else 'no'}",
        f"- **Documentaries:** {s.documentaries_measured or s.documentaries}  ·  "
        f"**Shots measured:** {s.measured_shots or s.shots}  ·  **Hours:** {s.hours:.1f}",
        "",
        "## Capability coverage matrix",
        "",
        "| Item | Kind | Corpus | Pipeline | Status | Obs | Conf |",
        "|------|------|-------:|----------|--------|----:|------|",
        *[f"| {r.name} | {r.kind} | "
          f"{'—' if r.corpus_fraction is None else f'{r.corpus_fraction:.0%}'} | {r.pipeline} | "
          f"{r.status} | {r.observations} | {r.confidence} |" for r in report.capability_matrix],
        "",
        "## Gaps (ranked by observed frequency)",
        "",
        "| # | Gap | Dimension | Freq | Obs | Conf | Severity |",
        "|--:|-----|-----------|-----:|----:|------|----------|",
        *[f"| {g.rank} | {g.title} | {g.dimension} | "
          f"{'—' if g.frequency is None else f'{g.frequency:.0%}'} | {g.observations} | "
          f"{g.confidence} | {g.severity} |" for g in report.gaps],
        "",
        "## Corpus completeness (under-represented → keep learning)",
        "",
        *([f"- **{c.dimension}/{c.category}** {c.fraction:.1%} ({c.observations} obs, {c.confidence}) — "
           f"{c.recommendation}" for c in report.completeness] or ["- (none)"]),
        "",
        "## Top discoveries",
        "",
        *([f"- [{d.confidence}] {d.statement}" for d in report.discoveries] or ["- (none)"]),
        "",
        "## Confidence (by sample size only)",
        "",
        *[f"- {n}" for n in report.confidence_notes],
        "",
        "## Notes",
        "",
        *[f"- {n}" for n in report.notes],
        "",
    ]
    return "\n".join(lines)
