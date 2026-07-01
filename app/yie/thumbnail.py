"""Análisis objetivo de la miniatura con Pillow (YIE).

Extrae SOLO atributos objetivos y deterministas: resolución, brillo, contraste,
saturación, temperatura de color, color dominante, estimación de % de texto (densidad
de bordes) e histogramas. NO detecta personas, NO usa CLIP ni modelos. Si no hay
miniatura o no se puede abrir, devuelve ``available=False`` (sin inventar).
"""

from app.yie import UNKNOWN
from app.yie.models import ThumbnailAnalysis

_EDGE_THRESHOLD = 40
_HIST_BINS = 16


def _reduce_histogram(values: list[int]) -> list[int]:
    step = 256 // _HIST_BINS
    return [sum(values[i * step:(i + 1) * step]) for i in range(_HIST_BINS)]


def analyze_thumbnail(path: str | None) -> ThumbnailAnalysis:
    if not path:
        return ThumbnailAnalysis(available=False)
    try:
        from PIL import Image, ImageFilter, ImageStat

        image = Image.open(path).convert("RGB")
    except Exception:
        return ThumbnailAnalysis(available=False)

    width, height = image.size
    gray = image.convert("L")
    gstat = ImageStat.Stat(gray)
    rgb_stat = ImageStat.Stat(image)
    r_mean, g_mean, b_mean = rgb_stat.mean
    sat = ImageStat.Stat(image.convert("HSV").getchannel(1))

    if r_mean > b_mean + 10:
        temperature = "warm"
    elif b_mean > r_mean + 10:
        temperature = "cool"
    else:
        temperature = "neutral"

    # color dominante (determinista): cuantización a 8 colores sobre versión reducida.
    small = image.resize((64, 64))
    quant = small.quantize(colors=8)
    palette = quant.getpalette() or []
    colors = quant.getcolors() or []
    dominant = UNKNOWN
    if colors and palette:
        index = max(colors)[1]
        r, g, b = palette[index * 3:index * 3 + 3]
        dominant = f"#{r:02x}{g:02x}{b:02x}"

    # estimación de texto/detalle: fracción de píxeles con borde fuerte.
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_hist = edges.histogram()                       # 256 cubos de intensidad
    strong = sum(edge_hist[_EDGE_THRESHOLD + 1:])
    text_pct = round(strong / (width * height), 4) if width and height else None

    r_hist, g_hist, b_hist = (
        image.getchannel("R").histogram(),
        image.getchannel("G").histogram(),
        image.getchannel("B").histogram(),
    )

    return ThumbnailAnalysis(
        available=True,
        width=width, height=height, resolution=f"{width}x{height}",
        brightness=round(gstat.mean[0] / 255.0, 4),
        contrast=round(gstat.stddev[0] / 255.0, 4),
        saturation=round(sat.mean[0] / 255.0, 4),
        color_temperature=temperature,
        dominant_color=dominant,
        text_percentage=text_pct,
        histogram={"r": _reduce_histogram(r_hist), "g": _reduce_histogram(g_hist),
                   "b": _reduce_histogram(b_hist)},
    )
