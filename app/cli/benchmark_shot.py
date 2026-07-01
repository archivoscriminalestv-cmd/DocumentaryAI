"""Benchmark de proveedores sobre un mismo plano (VPL-003).

    python -m app.cli.benchmark_shot                # todos los proveedores conocidos
    BENCHMARK_PROVIDERS=openai,imagen,mock python -m app.cli.benchmark_shot
    BENCHMARK_SHOT_INDEX=5 python -m app.cli.benchmark_shot

Compila el documental "Coquito" (VIS -> VAI -> VSC) y genera UN plano con varios
proveedores a la vez, comparando coste, tiempo, modelo y metadatos. Los proveedores
sin credenciales se marcan como no disponibles (no bloquean el resto).

Salida en ``output/benchmark/``: una imagen por proveedor con éxito + benchmark.json.
"""

import logging
import os
import sys

from app.cli.compile_coquito import build_requests
from app.vpl.benchmark import BenchmarkRunner, build_report
from app.vpl.config import PROVIDER_NAMES, make_provider, provider_capabilities


def run() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    raw = os.environ.get("BENCHMARK_PROVIDERS", "").strip()
    names = [p.strip().lower() for p in raw.split(",") if p.strip()] or list(PROVIDER_NAMES)
    names = [n for n in names if n in PROVIDER_NAMES]

    caps = provider_capabilities()
    print("[VPL] capacidades de proveedores:")
    for n in names:
        c = caps.get(n)
        if c:
            print(f"  - {n:<8} model={c.model:<26} cost=${c.cost_per_image:.4f} "
                  f"neg_nativo={c.native_negative_prompt} max={c.max_width}x{c.max_height} "
                  f"available={c.available}")

    requests = build_requests()
    index = int(os.environ.get("BENCHMARK_SHOT_INDEX", "0"))
    index = max(0, min(index, len(requests) - 1))
    request = requests[index]
    print(f"\n[Benchmark] shot={request.shot_id} (índice {index} de {len(requests)}) "
          f"-> proveedores {names}\n")

    providers = [make_provider(n) for n in names]
    report = BenchmarkRunner(providers).run(request, output_dir=os.path.join("output", "benchmark"))

    print(build_report(report))
    print(f"\nResultados: output/benchmark/  |  Informe: output/benchmark/benchmark.json")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
