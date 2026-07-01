"""Parser de entradas de la cola de aprendizaje (DLE-002B).

Convierte los argumentos de ``queue_add`` en una lista de URLs lista para encolar.
Acepta automáticamente:
- una URL suelta → un candidato,
- un fichero ``.txt`` → lee todas las URLs (ignora líneas vacías y comentarios ``#``),
- un directorio → busca todos los ``*.txt`` (recursivo) y los lee,
- una ruta de fichero local existente (no ``.txt``) → fuente local directa.

NUNCA encola el propio fichero ``.txt``. Valida las URLs, deduplica dentro del lote y
contra la cola y el índice de conocimiento (vía callbacks inyectables), y produce
estadísticas. No descarga ni modifica la cola: solo analiza y devuelve resultados.
"""

import glob
import os
from dataclasses import dataclass, field
from typing import Callable
from urllib.parse import urlparse


@dataclass
class ParseResult:
    found: int = 0                                  # candidatos vistos (sin vacíos/comentarios)
    added: list[str] = field(default_factory=list)  # URLs válidas, únicas y nuevas
    duplicates: int = 0                              # válidas pero repetidas / ya en cola / aprendidas
    invalid: list[str] = field(default_factory=list)
    sources_read: list[str] = field(default_factory=list)  # ficheros/rutas leídos
    missing: list[str] = field(default_factory=list)       # args no reconocidos (ni URL ni ruta)

    @property
    def valid(self) -> int:
        return len(self.added)


def is_valid_url(value: str) -> bool:
    # tolera BOM/espacios accidentales (ficheros guardados en Windows, etc.)
    cleaned = (value or "").strip().lstrip("﻿").strip()
    try:
        parsed = urlparse(cleaned)
    except Exception:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


class QueueInputParser:
    def __init__(
        self,
        *,
        existing: Callable[[str], bool] | None = None,   # ya en la cola
        learned: Callable[[str], bool] | None = None,    # ya en KnowledgeIndex
    ) -> None:
        self._existing = existing or (lambda url: False)
        self._learned = learned or (lambda url: False)

    def parse(self, inputs: list[str]) -> ParseResult:
        result = ParseResult()
        seen: set[str] = set()
        for arg in inputs:
            self._consume(arg, result, seen)
        return result

    # ------------------------------------------------------------------ interno
    def _consume(self, arg: str, result: ParseResult, seen: set[str]) -> None:
        arg = (arg or "").strip()
        if not arg:
            return
        if os.path.isdir(arg):
            for txt in sorted(glob.glob(os.path.join(arg, "**", "*.txt"), recursive=True)):
                result.sources_read.append(txt)
                self._read_txt(txt, result, seen)
        elif os.path.isfile(arg) and arg.lower().endswith(".txt"):
            result.sources_read.append(arg)
            self._read_txt(arg, result, seen)
        elif os.path.isfile(arg):
            # fuente local directa (p.ej. un vídeo): se mantiene el comportamiento DLE-002A
            result.sources_read.append(arg)
            self._add_candidate(arg, result, seen, is_path=True)
        elif is_valid_url(arg):
            self._add_candidate(arg, result, seen)
        else:
            # ni URL válida ni fichero/directorio existente: se reporta como NO encontrado
            # (no se cuenta como "URL inválida" para no ocultar un error de ruta/nombre).
            result.missing.append(arg)

    def _read_txt(self, path: str, result: ParseResult, seen: set[str]) -> None:
        try:
            with open(path, encoding="utf-8-sig") as handle:  # utf-8-sig: descarta BOM
                lines = list(handle)
        except OSError as exc:
            result.invalid.append(f"{path} (no se pudo leer: {exc})")
            return
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            self._add_candidate(stripped, result, seen)

    def _add_candidate(
        self, value: str, result: ParseResult, seen: set[str], *, is_path: bool = False
    ) -> None:
        result.found += 1
        if is_path:
            if not os.path.exists(value):
                result.invalid.append(value)
                return
        elif not is_valid_url(value):
            result.invalid.append(value)
            return
        if value in seen or self._existing(value) or self._learned(value):
            result.duplicates += 1
            return
        seen.add(value)
        result.added.append(value)
