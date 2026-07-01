"""Análisis visual por fotograma (determinista, solo Pillow).

Calcula brillo, contraste, temperatura de color, color dominante, iluminación y
día/noche. Lo que no es determinable con confianza se deja en UNKNOWN.
"""

import colorsys

from PIL import Image, ImageStat

from app.dle import UNKNOWN

_SAMPLE = (160, 90)


def _dominant_color_name(image: Image.Image) -> str:
    quant = image.resize((64, 36)).quantize(colors=5).convert("RGB")
    colors = quant.getcolors(64 * 36) or []
    if not colors:
        return UNKNOWN
    _count, (r, g, b) = max(colors, key=lambda c: c[0])
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if v < 0.15:
        return "black"
    if s < 0.12:
        return "white" if v > 0.7 else "gray"
    hue = h * 360
    buckets = (
        (15, "red"), (45, "orange"), (70, "yellow"), (165, "green"),
        (195, "cyan"), (255, "blue"), (300, "purple"), (345, "magenta"), (360, "red"),
    )
    for limit, name in buckets:
        if hue < limit:
            return name
    return "red"


def analyze_frame(frame_path: str) -> dict:
    with Image.open(frame_path) as raw:
        img = raw.convert("RGB").resize(_SAMPLE)
        gray = img.convert("L")
        gstat = ImageStat.Stat(gray)
        rstat = ImageStat.Stat(img)
        brightness = round(gstat.mean[0], 2)
        contrast = round(gstat.stddev[0], 2)
        r, g, b = (round(c, 2) for c in rstat.mean)
        dominant = _dominant_color_name(img)

    if r - b > 12:
        color_temp = "warm"
    elif b - r > 12:
        color_temp = "cool"
    else:
        color_temp = "neutral"

    if brightness < 70:
        lighting = "low-key"
    elif brightness > 150:
        lighting = "high-key"
    else:
        lighting = "balanced"

    if brightness < 55:
        day_night = "night"
    elif brightness > 110:
        day_night = "day"
    else:
        day_night = UNKNOWN

    return {"brightness": brightness, "contrast": contrast, "color_temperature": color_temp,
            "dominant_color": dominant, "lighting": lighting, "day_night": day_night,
            "rgb": (r, g, b)}
