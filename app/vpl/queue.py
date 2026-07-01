"""Ejecución concurrente del VPL — cola -> workers -> provider.

``WorkerPool.map`` ejecuta ``fn`` sobre los items en paralelo (hilos, apto para
I/O de proveedores) preservando el ORDEN de salida. La función por item NO debe
lanzar: debe devolver un resultado (éxito o fallo) para un manifest determinista.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable


class WorkerPool:
    def __init__(self, workers: int = 4) -> None:
        self._workers = max(1, int(workers))

    def map(self, fn: Callable, items: list) -> list:
        items = list(items)
        results: list = [None] * len(items)
        if not items:
            return results
        with ThreadPoolExecutor(max_workers=self._workers) as executor:
            futures = {executor.submit(fn, item): index for index, item in enumerate(items)}
            for future in as_completed(futures):
                results[futures[future]] = future.result()
        return results
