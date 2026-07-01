"""Modo benchmark del VPL (VPL-003).

Genera la MISMA petición visual con varios proveedores y registra, por cada
resultado, el coste, el tiempo (wall-clock real), el modelo y los metadatos. No
toca la cadena de planificación (VIS/VAI/VSC): consume exactamente el mismo
``VisualGenerationRequest`` que el orquestador y lo enruta a cada proveedor por
separado para poder compararlos lado a lado.

Salida (por defecto ``output/benchmark/``):
    {provider}.png            una imagen por proveedor que tuvo éxito
    {provider}.json           metadatos del resultado de ese proveedor
    benchmark.json            informe comparativo completo
"""

import hashlib
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field

from app.vpl.provider import ProviderError


@dataclass
class BenchmarkResult:
    provider: str
    model: str
    success: bool
    generation_time: float = 0.0   # wall-clock medido por el benchmark
    cost: float = 0.0
    width: int = 0
    height: int = 0
    image_hash: str = ""
    filename: str = ""
    available: bool = True
    error: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def resolution(self) -> str:
        return f"{self.width}x{self.height}"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["resolution"] = self.resolution
        return data


@dataclass
class BenchmarkReport:
    shot_id: str
    prompt: str
    providers: list[str]
    timestamp: str
    results: list[dict] = field(default_factory=list)

    @property
    def successes(self) -> int:
        return sum(1 for r in self.results if r.get("success"))

    @property
    def cheapest(self) -> str:
        ok = [r for r in self.results if r.get("success")]
        return min(ok, key=lambda r: r.get("cost", 0.0))["provider"] if ok else ""

    @property
    def fastest(self) -> str:
        ok = [r for r in self.results if r.get("success")]
        return min(ok, key=lambda r: r.get("generation_time", 0.0))["provider"] if ok else ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["successes"] = self.successes
        data["cheapest"] = self.cheapest
        data["fastest"] = self.fastest
        return data


class BenchmarkRunner:
    """Ejecuta un mismo request contra varios proveedores y compara resultados."""

    def __init__(self, providers: list, logger=None) -> None:
        self._providers = providers
        self._log = logger or logging.getLogger("vpl.benchmark")

    def run(self, request, *, output_dir: str = os.path.join("output", "benchmark"),
            timestamp: str = "") -> BenchmarkReport:
        os.makedirs(output_dir, exist_ok=True)
        results: list[BenchmarkResult] = []

        for provider in self._providers:
            results.append(self._run_one(provider, request, output_dir))

        report = BenchmarkReport(
            shot_id=str(getattr(request, "shot_id", "")),
            prompt=str(getattr(request, "prompt", "")),
            providers=[p.name for p in self._providers],
            timestamp=timestamp,
            results=[r.to_dict() for r in results],
        )
        with open(os.path.join(output_dir, "benchmark.json"), "w", encoding="utf-8") as handle:
            json.dump(report.to_dict(), handle, ensure_ascii=False, indent=2)
        return report

    def _run_one(self, provider, request, output_dir: str) -> BenchmarkResult:
        name = provider.name
        model = getattr(provider, "model", "")
        available = bool(getattr(provider, "is_available", lambda: True)())
        if not available:
            self._log.info("benchmark: '%s' no configurado, se omite", name)
            return BenchmarkResult(provider=name, model=model, success=False,
                                   available=False, error="proveedor no configurado")

        started = time.perf_counter()
        try:
            asset = provider.generate(request)
        except ProviderError as exc:
            return BenchmarkResult(provider=name, model=model, success=False,
                                   generation_time=round(time.perf_counter() - started, 3),
                                   error=str(exc))
        except Exception as exc:  # noqa: BLE001 — un adapter no debe tumbar el benchmark
            return BenchmarkResult(provider=name, model=model, success=False,
                                   generation_time=round(time.perf_counter() - started, 3),
                                   error=f"{type(exc).__name__}: {exc}")

        wall = round(time.perf_counter() - started, 3)
        image_bytes = asset.image_bytes or b""
        image_hash = hashlib.sha256(image_bytes).hexdigest()
        filename = f"{name}.png"
        with open(os.path.join(output_dir, filename), "wb") as handle:
            handle.write(image_bytes)
        meta = dict(asset.metadata) if isinstance(asset.metadata, dict) else {}
        result = BenchmarkResult(
            provider=name, model=asset.model or model, success=True,
            generation_time=wall, cost=asset.cost,
            width=asset.width, height=asset.height, image_hash=image_hash,
            filename=filename, available=True, metadata=meta,
        )
        with open(os.path.join(output_dir, f"{name}.json"), "w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, ensure_ascii=False, indent=2)
        return result


def build_report(report: BenchmarkReport) -> str:
    """Tabla comparativa legible de un BenchmarkReport."""
    header = f"{'Provider':<10} {'Model':<26} {'OK':<4} {'Time':>8} {'Cost':>9} {'Resolution':>12}"
    lines = ["Benchmark", "", f"Shot: {report.shot_id}", "", header, "-" * len(header)]
    for r in report.results:
        ok = "yes" if r.get("success") else ("n/a" if not r.get("available") else "no")
        lines.append(
            f"{r['provider']:<10} {str(r.get('model',''))[:26]:<26} {ok:<4} "
            f"{r.get('generation_time',0.0):>7.2f}s ${r.get('cost',0.0):>7.4f} "
            f"{r.get('resolution',''):>12}"
        )
    lines += ["", f"Successes: {report.successes}/{len(report.results)}"]
    if report.fastest:
        lines.append(f"Fastest:   {report.fastest}")
    if report.cheapest:
        lines.append(f"Cheapest:  {report.cheapest}")
    return "\n".join(lines)
