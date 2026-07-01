"""Selección determinista compartida por los motores de VAI.

``rotate`` elige de forma determinista en función del índice del plano (+offset
por categoría) para que planos contiguos varíen sin azar (anti-repetición), de
acuerdo con ARCH-VIS-000 §13.
"""


def rotate(options: list[str], index: int, offset: int = 0) -> str:
    if not options:
        return ""
    return options[(index + offset) % len(options)]
