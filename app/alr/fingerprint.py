"""Huellas de imagen para el ALR (deterministas, sin dependencias extra).

- ``sha256_bytes``  : identidad exacta del binario (deduplicación exacta).
- ``average_hash``  : aHash 8x8 (similitud rápida).
- ``perceptual_hash``: pHash 8x8 vía DCT (similitud robusta a recompresión/escala).
- ``hamming``       : distancia entre dos huellas hex de igual longitud.

Pillow ya es dependencia del proyecto. El DCT se implementa en Python puro para no
añadir numpy/scipy y mantener el resultado reproducible.
"""

import hashlib
import io
import math

from PIL import Image

_DCT_CACHE: dict[int, list[list[float]]] = {}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bits_to_hex(bits: list[bool]) -> str:
    value = 0
    for bit in bits:
        value = (value << 1) | (1 if bit else 0)
    width = (len(bits) + 3) // 4
    return f"{value:0{width}x}"


def _open_gray(data: bytes, size: int) -> list[list[float]]:
    with Image.open(io.BytesIO(data)) as img:
        small = img.convert("L").resize((size, size), Image.LANCZOS)
        flat = list(small.getdata())
    return [[float(flat[r * size + c]) for c in range(size)] for r in range(size)]


def average_hash(data: bytes, hash_size: int = 8) -> str:
    matrix = _open_gray(data, hash_size)
    pixels = [v for row in matrix for v in row]
    avg = sum(pixels) / len(pixels)
    return _bits_to_hex([p > avg for p in pixels])


def _dct_matrix(n: int) -> list[list[float]]:
    cached = _DCT_CACHE.get(n)
    if cached is not None:
        return cached
    matrix = [[0.0] * n for _ in range(n)]
    factor = math.pi / (2 * n)
    for u in range(n):
        cu = math.sqrt(1.0 / n) if u == 0 else math.sqrt(2.0 / n)
        for x in range(n):
            matrix[u][x] = cu * math.cos((2 * x + 1) * u * factor)
    _DCT_CACHE[n] = matrix
    return matrix


def _dct2d(matrix: list[list[float]], n: int) -> list[list[float]]:
    d = _dct_matrix(n)
    # temp = D · M
    temp = [[sum(d[u][k] * matrix[k][x] for k in range(n)) for x in range(n)] for u in range(n)]
    # out = temp · Dᵀ
    return [[sum(temp[u][k] * d[v][k] for k in range(n)) for v in range(n)] for u in range(n)]


def perceptual_hash(data: bytes, hash_size: int = 8, highfreq_factor: int = 4) -> str:
    n = hash_size * highfreq_factor
    matrix = _open_gray(data, n)
    dct = _dct2d(matrix, n)
    low = [dct[u][v] for u in range(hash_size) for v in range(hash_size)]
    # Mediana excluyendo el término DC (low[0]) para fijar el umbral.
    rest = sorted(low[1:])
    mid = len(rest) // 2
    median = rest[mid] if len(rest) % 2 else (rest[mid - 1] + rest[mid]) / 2
    return _bits_to_hex([v > median for v in low])


def hamming(a: str, b: str) -> int:
    """Distancia de Hamming entre dos huellas hex de igual longitud."""
    if not a or not b or len(a) != len(b):
        return max(len(a), len(b)) * 4  # incomparables -> distancia máxima
    return bin(int(a, 16) ^ int(b, 16)).count("1")


def image_properties(data: bytes) -> tuple[int, int, str]:
    with Image.open(io.BytesIO(data)) as img:
        return img.width, img.height, (img.format or "PNG")
