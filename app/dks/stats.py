"""Funciones estadísticas puras y deterministas (DKS).

Sin dependencias externas (sin numpy). Solo agregan datos; nunca infieren. Todas
redondean a 4 decimales para reproducibilidad estable entre ejecuciones.
"""

import math

_ND = 4


def _round(x: float) -> float:
    return round(float(x), _ND)


def mean(values) -> float:
    xs = [float(v) for v in values]
    return _round(sum(xs) / len(xs)) if xs else 0.0


def median(values) -> float:
    xs = sorted(float(v) for v in values)
    if not xs:
        return 0.0
    n = len(xs)
    mid = n // 2
    return _round(xs[mid] if n % 2 else (xs[mid - 1] + xs[mid]) / 2.0)


def stdev(values) -> float:
    xs = [float(v) for v in values]
    if len(xs) < 2:
        return 0.0
    mu = sum(xs) / len(xs)
    var = sum((x - mu) ** 2 for x in xs) / len(xs)   # poblacional (determinista)
    return _round(math.sqrt(var))


def summarize(values) -> dict:
    xs = [float(v) for v in values]
    return {
        "count": len(xs),
        "mean": mean(xs),
        "median": median(xs),
        "min": _round(min(xs)) if xs else 0.0,
        "max": _round(max(xs)) if xs else 0.0,
        "stdev": stdev(xs),
    }


def merge_counts(dicts) -> dict:
    """Suma varios diccionarios {etiqueta: conteo} en uno (ordenado por etiqueta)."""
    total: dict[str, int] = {}
    for d in dicts:
        for key, value in (d or {}).items():
            total[key] = total.get(key, 0) + int(value)
    return {k: total[k] for k in sorted(total)}


def normalize(counts: dict) -> dict:
    """{etiqueta: conteo} -> {etiqueta: fracción 0..1} (ordenado, reproducible)."""
    total = sum(counts.values())
    if total <= 0:
        return {k: 0.0 for k in sorted(counts)}
    return {k: _round(counts[k] / total) for k in sorted(counts)}


def distribution(dicts) -> dict:
    """Devuelve conteos agregados + fracciones normalizadas."""
    counts = merge_counts(dicts)
    return {"counts": counts, "fractions": normalize(counts), "total": sum(counts.values())}


def histogram(values, bins: int = 10) -> list[dict]:
    """Histograma de bins uniformes sobre [min, max]. Determinista."""
    xs = [float(v) for v in values]
    if not xs:
        return []
    lo, hi = min(xs), max(xs)
    if lo == hi:
        return [{"range": [_round(lo), _round(hi)], "count": len(xs)}]
    width = (hi - lo) / bins
    edges = [lo + i * width for i in range(bins + 1)]
    counts = [0] * bins
    for x in xs:
        idx = int((x - lo) / width)
        if idx >= bins:           # el máximo cae en el último bin
            idx = bins - 1
        counts[idx] += 1
    return [{"range": [_round(edges[i]), _round(edges[i + 1])], "count": counts[i]}
            for i in range(bins)]


def pearson(xs, ys):
    """Correlación de Pearson de pares (xs, ys). None si no hay varianza/datos."""
    xs = [float(v) for v in xs]
    ys = [float(v) for v in ys]
    n = min(len(xs), len(ys))
    if n < 2:
        return None
    xs, ys = xs[:n], ys[:n]
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    return _round(cov / math.sqrt(vx * vy))
