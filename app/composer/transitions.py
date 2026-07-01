"""Transiciones del Composer (decididas por el Timeline, no por el Composer).

Se ejecutan como fundidos por clip (no solapados) para preservar la sincronía exacta
audio/vídeo: el primer clip entra con fade-in, el último sale con fade-out, y entre
clips un fade-out+fade-in corto produce un disolución suave (dissolve).
"""

_EDGE = 1.0      # fade in del primer plano / fade out del último
_CUT = 0.4       # disolución entre planos


def decide(index: int, total: int) -> dict:
    first = index == 0
    last = index == total - 1
    return {
        "transition_in": "fade_in" if first else "dissolve",
        "fade_in": _EDGE if first else _CUT,
        "transition_out": "fade_out" if last else "dissolve",
        "fade_out": _EDGE if last else _CUT,
    }
