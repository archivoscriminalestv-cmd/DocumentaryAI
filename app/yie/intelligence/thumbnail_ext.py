"""Análisis extendido de la miniatura (YIE-002) — Pillow, solo atributos OBJETIVOS.

Añade aspect ratio, paleta/colores dominantes, densidad de bordes, % de texto estimado
(densidad de bordes) y bordes en el margen exterior. NUNCA detecta personas, NUNCA
infiere emociones, NUNCA usa CLIP ni modelos. La imagen se analiza y se descarta (no se
conserva).
"""

from app.yie import UNKNOWN
from app.yie.intelligence.models import ExtendedThumbnail

_EDGE_THRESHOLD = 40
_HIST_BINS = 16


def _reduce(values: list[int]) -> list[int]:
    step = 256 // _HIST_BINS
    return [sum(values[i * step:(i + 1) * step]) for i in range(_HIST_BINS)]


def analyze_thumbnail_extended(path: str | None) -> ExtendedThumbnail:
    if not path:
        return ExtendedThumbnail(available=False)
    try:
        from PIL import Image, ImageFilter, ImageStat

        image = Image.open(path).convert("RGB")
    except Exception:
        return ExtendedThumbnail(available=False)

    width, height = image.size
    gray = image.convert("L")
    gstat = ImageStat.Stat(gray)
    r_mean, g_mean, b_mean = ImageStat.Stat(image).mean
    sat = ImageStat.Stat(image.convert("HSV").getchannel(1)).mean[0]

    if r_mean > b_mean + 10:
        temperature = "warm"
    elif b_mean > r_mean + 10:
        temperature = "cool"
    else:
        temperature = "neutral"

    # paleta de color (determinista): 5 colores sobre versión reducida.
    small = image.resize((64, 64))
    quant = small.quantize(colors=5)
    palette = quant.getpalette() or []
    colors = sorted(quant.getcolors() or [], reverse=True)   # [(count, idx)] desc
    total_px = sum(count for count, _ in colors) or 1
    color_palette = []
    for count, idx in colors:
        r, g, b = palette[idx * 3:idx * 3 + 3]
        color_palette.append({"color": f"#{r:02x}{g:02x}{b:02x}",
                              "fraction": round(count / total_px, 4)})
    dominant_colors = [entry["color"] for entry in color_palette[:3]]

    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_hist = edges.histogram()
    total_strong = sum(edge_hist[_EDGE_THRESHOLD + 1:])
    edge_density = round(ImageStat.Stat(edges).mean[0] / 255.0, 4)
    text_pct = round(total_strong / (width * height), 4) if width and height else None

    center = edges.crop((int(width * 0.1), int(height * 0.1),
                         int(width * 0.9), int(height * 0.9)))
    center_strong = sum(center.histogram()[_EDGE_THRESHOLD + 1:])
    safe_margin_ratio = (
        round((total_strong - center_strong) / total_strong, 4) if total_strong else None
    )

    return ExtendedThumbnail(
        available=True,
        width=width, height=height,
        aspect_ratio=round(width / height, 4) if height else None,
        brightness=round(gstat.mean[0] / 255.0, 4),
        contrast=round(gstat.stddev[0] / 255.0, 4),
        average_saturation=round(sat / 255.0, 4),
        color_temperature=temperature,
        dominant_colors=dominant_colors,
        color_palette=color_palette,
        edge_density=edge_density,
        text_area_percentage=text_pct,
        safe_margin_edge_ratio=safe_margin_ratio,
        histogram={"r": _reduce(image.getchannel("R").histogram()),
                   "g": _reduce(image.getchannel("G").histogram()),
                   "b": _reduce(image.getchannel("B").histogram())},
    )
