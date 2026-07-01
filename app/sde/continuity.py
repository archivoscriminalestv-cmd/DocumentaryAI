"""Salvaguardas de continuidad e identidad del SDE.

El SDE puede cambiar ángulo/posición/lente/altura/encuadre, pero NUNCA la identidad
del personaje ni la continuidad de escena (localización, paleta, hora, clima, luz).
Estas funciones verifican esa invariante; son la red de seguridad del subsistema.
"""

from app.sde.models import ShotFingerprint

# Dimensiones que el SDE tiene PROHIBIDO modificar (identidad + look de escena).
IMMUTABLE_DIMENSIONS = ("scene", "character", "identity", "location", "color_palette",
                        "time_of_day", "weather", "lighting_language")


def identity_preserved(base: ShotFingerprint, final: ShotFingerprint) -> bool:
    return all(getattr(base, d) == getattr(final, d) for d in IMMUTABLE_DIMENSIONS)


def assert_identity_preserved(base: ShotFingerprint, final: ShotFingerprint) -> None:
    for d in IMMUTABLE_DIMENSIONS:
        if getattr(base, d) != getattr(final, d):
            raise ValueError(
                f"SDE rompió una dimensión inmutable '{d}': "
                f"{getattr(base, d)!r} -> {getattr(final, d)!r}"
            )
