"""Análisis determinista corpus ↔ pipeline (ADV-002).

Compara las distribuciones MEDIDAS del corpus (DKS) con las capacidades conocidas del
pipeline. Sin IA, sin pesos arbitrarios: el ranking de impacto se basa solo en la
frecuencia observada y la confianza solo en el tamaño muestral. Nunca inventa: lo no
medido queda como UNKNOWN.
"""

from app.advisor import UNKNOWN
from app.advisor.models import (
    DIMENSIONS,
    SHOT_CONFIDENCE,
    DOC_CONFIDENCE,
    CapabilityMatrixRow,
    CompletenessFinding,
    CorpusSnapshot,
    CoverageStatus,
    Dimension,
    Discovery,
    GapFinding,
    Recommendation,
    Severity,
    _DIMENSION_PIPELINE_SUPPORT,
    confidence_from,
)

_CAPABILITY_DIMS = {"shot_size", "composition"}   # dims que son "capacidad de análisis"


def _non_unknown(dist: dict) -> dict:
    return {k: v for k, v in dist.get("fractions", {}).items() if k != "UNKNOWN"}


def _shot_conf(n: int) -> str:
    return confidence_from(n, **SHOT_CONFIDENCE)


# --- 1) Capability Coverage Matrix -------------------------------------------

def build_capability_matrix(snapshot: CorpusSnapshot) -> list[CapabilityMatrixRow]:
    rows: list[CapabilityMatrixRow] = []
    for dim in DIMENSIONS:
        dist = snapshot.dimensions.get(dim)
        pipeline = _DIMENSION_PIPELINE_SUPPORT.get(dim, "yes")
        if not dist:
            rows.append(CapabilityMatrixRow(name=dim, kind="dimension", pipeline=pipeline,
                                            status=CoverageStatus.UNKNOWN, note="sin datos"))
            continue
        nu = _non_unknown(dist)
        coverage = round(sum(nu.values()), 4)
        observed = coverage > 0.0
        total = dist.get("total", 0)
        if not observed:
            status = CoverageStatus.UNKNOWN
        elif pipeline == "yes":
            status = CoverageStatus.SUPPORTED
        elif pipeline == "no":
            status = CoverageStatus.MISSING
        else:
            status = CoverageStatus.UNKNOWN
        rows.append(CapabilityMatrixRow(
            name=dim, kind="dimension", corpus_observed=observed,
            corpus_fraction=coverage if observed else None, observations=total,
            pipeline=pipeline, status=status, confidence=_shot_conf(total),
            note="" if observed else "corpus sin detector (mayoría UNKNOWN)"))

    for cap in snapshot.capabilities:
        pipeline = cap.pipeline_supported
        status = (CoverageStatus.MISSING if pipeline == "no"
                  else CoverageStatus.SUPPORTED if pipeline == "yes"
                  else CoverageStatus.UNKNOWN)
        rows.append(CapabilityMatrixRow(
            name=cap.capability, kind="capability", corpus_observed=False,
            corpus_fraction=None, observations=0, pipeline=pipeline, status=status,
            confidence="LOW", note="sin señal pública en el corpus"))
    return rows


# --- 2) Gap Analyzer ----------------------------------------------------------

class CorpusGapAnalyzer:
    def analyze(self, snapshot: CorpusSnapshot,
                matrix: list[CapabilityMatrixRow] | None = None) -> list[GapFinding]:
        matrix = matrix if matrix is not None else build_capability_matrix(snapshot)
        gaps: list[GapFinding] = []

        if not snapshot.available:
            gaps.append(GapFinding(
                id="corpus.empty", title="Aún no hay corpus legible",
                dimension=Dimension.CAPABILITY, severity=Severity.INFO,
                rationale="No se encontraron artefactos públicos en knowledge/.",
                frequency=None, observations=0, confidence="LOW"))
            return gaps

        # (a) Blind spots: dimensiones que el corpus apenas mide (≥50% UNKNOWN).
        for dim in DIMENSIONS:
            dist = snapshot.dimensions.get(dim)
            if not dist:
                continue
            total = dist.get("total", 0)
            uf = round(dist.get("fractions", {}).get("UNKNOWN", 0.0), 4)
            if uf >= 0.5:
                gaps.append(GapFinding(
                    id=f"blindspot.{dim}", title=f"El corpus no mide '{dim}'",
                    dimension=Dimension.CAPABILITY if dim in _CAPABILITY_DIMS else dim,
                    severity=Severity.MAJOR, corpus_value=f"{uf:.0%} UNKNOWN",
                    pipeline_value=_DIMENSION_PIPELINE_SUPPORT.get(dim, "yes"),
                    rationale=f"{uf:.0%} de {total} planos sin valor de '{dim}': "
                              f"no hay base para comparar con el pipeline.",
                    frequency=uf, observations=total, confidence=_shot_conf(total)))

        # (b) Categoría medida y frecuente que el pipeline NO produce (regla genérica).
        for row in matrix:
            if row.kind != "dimension" or not row.corpus_observed or row.pipeline != "no":
                continue
            dist = snapshot.dimensions.get(row.name, {})
            for cat, frac in _non_unknown(dist).items():
                gaps.append(GapFinding(
                    id=f"category.{row.name}.{cat}",
                    title=f"El pipeline no cubre '{cat}' en {row.name}",
                    dimension=row.name, severity=Severity.MAJOR,
                    corpus_value=cat, pipeline_value="no",
                    rationale=f"'{cat}' aparece en {frac:.0%} del corpus pero el pipeline no lo produce.",
                    frequency=round(frac, 4),
                    observations=dist.get("counts", {}).get(cat, 0),
                    confidence=_shot_conf(dist.get("total", 0))))

        # (c) Capacidades de producción ausentes del pipeline (hecho), sin cuantificar.
        for row in matrix:
            if row.kind == "capability" and row.status == CoverageStatus.MISSING:
                gaps.append(GapFinding(
                    id=f"capability.{row.name}", title=f"El pipeline no produce '{row.name}'",
                    dimension=Dimension.CAPABILITY, severity=Severity.MINOR,
                    corpus_value=UNKNOWN, pipeline_value="no",
                    rationale="Capacidad ausente en la generación; cobertura del corpus "
                              "desconocida (sin señal pública todavía).",
                    frequency=None, observations=0, confidence="LOW"))
        return gaps


# --- 3) Impact Ranking (solo por frecuencia observada) -----------------------

def rank_gaps(gaps: list[GapFinding]) -> list[GapFinding]:
    quantified = sorted([g for g in gaps if g.frequency is not None],
                        key=lambda g: (-g.frequency, g.id))
    unquantified = sorted([g for g in gaps if g.frequency is None], key=lambda g: g.id)
    ordered = quantified + unquantified
    for i, g in enumerate(ordered, start=1):
        g.rank = i
    return ordered


# --- 4) Corpus Completeness ---------------------------------------------------

def analyze_completeness(snapshot: CorpusSnapshot) -> list[CompletenessFinding]:
    findings: list[CompletenessFinding] = []
    for dim in DIMENSIONS:
        dist = snapshot.dimensions.get(dim)
        if not dist:
            continue
        nu = _non_unknown(dist)
        if len(nu) < 2:
            continue
        mean = sum(nu.values()) / len(nu)
        total = dist.get("total", 0)
        for cat, frac in sorted(nu.items(), key=lambda kv: (kv[1], kv[0])):
            if frac < 0.5 * mean:               # regla de datos: < mitad de la media
                findings.append(CompletenessFinding(
                    dimension=dim, category=cat, fraction=round(frac, 4),
                    observations=dist.get("counts", {}).get(cat, 0),
                    confidence=_shot_conf(total),
                    recommendation=f"Aprender más documentales con '{cat}' en {dim} "
                                   f"(infrarrepresentado: {frac:.1%} vs media {mean:.1%})."))
    return findings


# --- 5)+6) Confidence + Top Discoveries --------------------------------------

def find_discoveries(snapshot: CorpusSnapshot, limit: int = 12) -> list[Discovery]:
    disc: list[Discovery] = []
    for dim in DIMENSIONS:
        dist = snapshot.dimensions.get(dim)
        if not dist:
            continue
        total = dist.get("total", 0)
        nu = _non_unknown(dist)
        uf = dist.get("fractions", {}).get("UNKNOWN", 0.0)
        if nu:
            cat, frac = max(nu.items(), key=lambda kv: (kv[1], kv[0]))
            disc.append(Discovery(
                id=f"dominant.{dim}", dimension=dim, value=cat, fraction=round(frac, 4),
                observations=total, confidence=_shot_conf(total),
                statement=f"En '{dim}' domina '{cat}' ({frac:.0%} de {total} planos)."))
        if uf >= 0.5:
            disc.append(Discovery(
                id=f"unmeasured.{dim}", dimension=dim, value="UNKNOWN", fraction=round(uf, 4),
                observations=total, confidence=_shot_conf(total),
                statement=f"'{dim}' no se mide en el corpus ({uf:.0%} UNKNOWN)."))
    for key, stat in snapshot.numeric.items():
        if stat.get("mean") is None:
            continue
        n = int(stat.get("count", 0) or 0)
        disc.append(Discovery(
            id=f"numeric.{key}", dimension=key, value=str(stat.get("mean")), fraction=None,
            observations=n, confidence=confidence_from(n, **DOC_CONFIDENCE),
            statement=f"{key}: media {stat.get('mean')}, mediana {stat.get('median')}, "
                      f"máx {stat.get('max')} (n={n})."))
    disc.sort(key=lambda d: (-d.observations, -(d.fraction or 0.0), d.id))
    return disc[:limit]


def confidence_notes(snapshot: CorpusSnapshot) -> list[str]:
    notes = []
    for dim in DIMENSIONS:
        dist = snapshot.dimensions.get(dim)
        if dist:
            n = dist.get("total", 0)
            notes.append(f"{dim}: {n} observaciones → {_shot_conf(n)}")
    docs = snapshot.documentaries_measured or snapshot.documentaries
    notes.append(f"corpus: {docs} documentales → {confidence_from(docs, **DOC_CONFIDENCE)}")
    return notes


# --- recomendaciones derivadas de los gaps (prioridad = frecuencia, sin subjetividad) ---

class CorpusRecommender:
    def recommend(self, snapshot: CorpusSnapshot, gaps: list[GapFinding]) -> list[Recommendation]:
        recs: list[Recommendation] = []
        for g in gaps:
            recs.append(Recommendation(
                id=f"act.{g.id}", title=f"Atender: {g.title}",
                impact="UNKNOWN", effort="UNKNOWN",
                priority=round(g.frequency, 4) if g.frequency is not None else 0.0,
                rationale="Prioridad = frecuencia observada en el corpus (sin scoring "
                          "subjetivo). Impacto/esfuerzo pendientes de datos de capacidad.",
                addresses=[g.id]))
        recs.sort(key=lambda r: (-r.priority, r.id))
        return recs
