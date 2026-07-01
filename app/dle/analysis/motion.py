"""Estimación de movimiento entre dos fotogramas (determinista, Pillow).

Mide la diferencia media de píxeles (cámara + sujeto) y la clasifica. No distingue
tipo de movimiento de cámara (eso requeriría flujo óptico): clasifica intensidad.
"""

from PIL import Image, ImageChops, ImageStat

from app.dle import UNKNOWN

_SAMPLE = (160, 90)


def analyze_motion(frame_a: str | None, frame_b: str | None) -> tuple[float, str]:
    if not frame_a or not frame_b:
        return 0.0, UNKNOWN
    with Image.open(frame_a) as ra, Image.open(frame_b) as rb:
        a = ra.convert("L").resize(_SAMPLE)
        b = rb.convert("L").resize(_SAMPLE)
        diff = ImageChops.difference(a, b)
        mag = round(ImageStat.Stat(diff).mean[0], 3)
    if mag < 2.0:
        return mag, "static"
    if mag < 8.0:
        return mag, "subtle"
    if mag < 20.0:
        return mag, "moderate"
    return mag, "dynamic"
