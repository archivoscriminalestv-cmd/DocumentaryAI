"""Detectores de visión CLÁSICA del VUE (VUE-002).

Solo técnicas clásicas y deterministas con Pillow + matemáticas (sin IA, sin Deep
Learning, sin OpenCV/numpy — no instalados y prohibidos por el guard del paquete). Cada
detector mide HECHOS objetivos; nunca interpreta intención artística ni clasifica más allá
de lo medible. Nunca lanza excepción: ante cualquier problema devuelve UNKNOWN.

Nota: Canny requiere OpenCV; aquí se usa el filtro clásico de bordes de Pillow
(FIND_EDGES) + umbral, equivalente clásico determinista para densidad de bordes.
"""

import colorsys

from PIL import Image, ImageChops, ImageFilter, ImageStat

from app.vue import NOT_IMPLEMENTED, UNKNOWN
from app.vue.interfaces import FrameRef
from app.vue.models import VisualObservation

_METHOD = "classical_cv"
_EDGE_THRESHOLD = 40
_WORK = (256, 144)     # tamaño de trabajo fijo (determinismo)
_SMALL = (64, 36)      # para centroides/balance


def _load(path: str, size: tuple[int, int] | None = None) -> Image.Image | None:
    if not path:
        return None
    try:
        img = Image.open(path).convert("RGB")
        return img.resize(size, Image.BILINEAR) if size else img
    except Exception:
        return None


def _obs(detector: str, capability: str, value=UNKNOWN, facts=None,
         method=_METHOD) -> VisualObservation:
    return VisualObservation(detector=detector, capability=capability, value=value,
                             confidence=None, facts=facts or {}, method=method)


def _unknown(detector: str, capability: str, note: str = "") -> VisualObservation:
    return _obs(detector, capability, value=UNKNOWN,
                facts={"note": note or "no medible"}, method=NOT_IMPLEMENTED)


def _edge_density(gray: Image.Image, threshold: int = _EDGE_THRESHOLD) -> float:
    edges = gray.filter(ImageFilter.FIND_EDGES)
    binary = edges.point(lambda p: 255 if p > threshold else 0)
    hist = binary.histogram()
    total = sum(hist) or 1
    return round(hist[255] / total, 4)


def _color_name(r: float, g: float, b: float) -> str:
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if v < 0.15:
        return "black"
    if s < 0.12:
        return "white" if v > 0.7 else "gray"
    hue = h * 360
    for limit, name in ((15, "red"), (45, "orange"), (70, "yellow"), (165, "green"),
                        (195, "cyan"), (255, "blue"), (300, "purple"), (345, "magenta"), (360, "red")):
        if hue < limit:
            return name
    return "red"


# --- 1) Composition (solo geometría; nunca intención artística) --------------

class CompositionDetector:
    capability = "composition"

    def detect(self, frame: FrameRef, context: dict | None = None) -> VisualObservation:
        img = _load(frame.path, _SMALL)
        if img is None:
            return _unknown(type(self).__name__, self.capability, "frame no legible")
        try:
            gray = img.convert("L")
            w, h = gray.size
            data = list(gray.getdata())
            total_mass = sum(data) or 1
            sx = sum(p * (i % w) for i, p in enumerate(data))
            sy = sum(p * (i // w) for i, p in enumerate(data))
            cx = sx / total_mass / (w - 1)
            cy = sy / total_mass / (h - 1)
            left = sum(p for i, p in enumerate(data) if (i % w) < w / 2)
            top = sum(p for i, p in enumerate(data) if (i // w) < h / 2)
            lr = round(left / total_mass, 4)
            tb = round(top / total_mass, 4)
            thirds_x = round(min(abs(cx - 1 / 3), abs(cx - 2 / 3)), 4)
            thirds_y = round(min(abs(cy - 1 / 3), abs(cy - 2 / 3)), 4)
            negative_space = round(1.0 - _edge_density(gray), 4)
            facts = {
                "center_x": round(cx, 4), "center_y": round(cy, 4),
                "left_right_balance": lr, "top_bottom_balance": tb,
                "thirds_offset_x": thirds_x, "thirds_offset_y": thirds_y,
                "negative_space": negative_space,
            }
            return _obs(type(self).__name__, self.capability, value=UNKNOWN, facts=facts)
        except Exception:
            return _unknown(type(self).__name__, self.capability, "error de cálculo")


# --- 2) Color analysis -------------------------------------------------------

class ColorAnalysisDetector:
    capability = "color"

    def detect(self, frame: FrameRef, context: dict | None = None) -> VisualObservation:
        img = _load(frame.path, _WORK)
        if img is None:
            return _unknown(type(self).__name__, self.capability, "frame no legible")
        try:
            stat = ImageStat.Stat(img)
            r, g, b = (round(c, 2) for c in stat.mean)
            gray = img.convert("L")
            gstat = ImageStat.Stat(gray)
            brightness = round(gstat.mean[0], 2)
            contrast = round(gstat.stddev[0], 2)
            sat = round(ImageStat.Stat(img.convert("HSV")).mean[1] / 255.0, 4)
            temp = "warm" if r - b > 12 else "cool" if b - r > 12 else "neutral"

            quant = img.resize((48, 27)).quantize(colors=5).convert("RGB")
            colors = sorted(quant.getcolors(48 * 27) or [], key=lambda c: -c[0])
            palette = [_color_name(*rgb) for _n, rgb in colors[:3]]
            dominant = palette[0] if palette else UNKNOWN

            ghist = gray.histogram()
            tot = sum(ghist) or 1
            shadows = round(sum(ghist[0:5]) / tot, 4)
            highlights = round(sum(ghist[250:256]) / tot, 4)
            rgb_hist = {ch: _bins(img.getchannel(ch).histogram())
                        for ch in ("R", "G", "B")}
            facts = {
                "dominant_color": dominant, "palette": palette, "temperature": temp,
                "saturation": sat, "contrast": contrast, "brightness": brightness,
                "exposure": {"clipped_shadows": shadows, "clipped_highlights": highlights},
                "rgb_mean": {"r": r, "g": g, "b": b}, "rgb_histogram": rgb_hist,
            }
            return _obs(type(self).__name__, self.capability, value=dominant, facts=facts)
        except Exception:
            return _unknown(type(self).__name__, self.capability, "error de cálculo")


def _bins(hist256: list[int], bins: int = 8) -> list[int]:
    step = 256 // bins
    return [sum(hist256[i * step:(i + 1) * step]) for i in range(bins)]


# --- 3) Edge density ---------------------------------------------------------

class EdgeDensityDetector:
    capability = "edge_density"

    def detect(self, frame: FrameRef, context: dict | None = None) -> VisualObservation:
        img = _load(frame.path, _WORK)
        if img is None:
            return _unknown(type(self).__name__, self.capability, "frame no legible")
        try:
            gray = img.convert("L")
            density = _edge_density(gray)
            w, h = gray.size
            grid, busiest, busiest_val = [], 0, -1.0
            for gy in range(3):
                row = []
                for gx in range(3):
                    cell = gray.crop((gx * w // 3, gy * h // 3,
                                      (gx + 1) * w // 3, (gy + 1) * h // 3))
                    d = _edge_density(cell)
                    row.append(d)
                    if d > busiest_val:
                        busiest_val, busiest = d, gy * 3 + gx
                grid.append(row)
            facts = {
                "edge_density": density, "texture_pct": round(density * 100, 2),
                "complexity": density, "detail_grid": grid, "busiest_cell": busiest,
            }
            return _obs(type(self).__name__, self.capability, value=UNKNOWN, facts=facts)
        except Exception:
            return _unknown(type(self).__name__, self.capability, "error de cálculo")


# --- 4) Motion energy (dos frames; sin clasificar el movimiento) -------------

class MotionEnergyDetector:
    capability = "motion_energy"

    def detect(self, frame: FrameRef, context: dict | None = None) -> VisualObservation:
        prev_path = self._previous_path(context)
        if not prev_path:
            return _unknown(type(self).__name__, self.capability, "sin frame previo")
        cur = _load(frame.path, _WORK)
        prev = _load(prev_path, _WORK)
        if cur is None or prev is None:
            return _unknown(type(self).__name__, self.capability, "frame no legible")
        try:
            gcur, gprev = cur.convert("L"), prev.convert("L")
            diff = ImageChops.difference(gcur, gprev)
            abs_mean = round(ImageStat.Stat(diff).mean[0], 4)
            hist = diff.histogram()
            tot = sum(hist) or 1
            changed = round(sum(hist[16:]) / tot, 4)          # píxeles con cambio > 16
            facts = {
                "abs_diff_mean": abs_mean, "changed_pixel_pct": changed,
                "intensity": round(abs_mean / 255.0, 4),
            }
            return _obs(type(self).__name__, self.capability, value=UNKNOWN, facts=facts)
        except Exception:
            return _unknown(type(self).__name__, self.capability, "error de cálculo")

    @staticmethod
    def _previous_path(context: dict | None) -> str:
        if not context:
            return ""
        prev = context.get("previous_frame") or context.get("previous_path")
        if isinstance(prev, FrameRef):
            return prev.path
        return prev if isinstance(prev, str) else ""


# --- 5) Frame geometry -------------------------------------------------------

class FrameGeometryDetector:
    capability = "frame_geometry"

    def detect(self, frame: FrameRef, context: dict | None = None) -> VisualObservation:
        try:
            with Image.open(frame.path) as raw:
                width, height = raw.size
        except Exception:
            return _unknown(type(self).__name__, self.capability, "frame no legible")
        if not width or not height:
            return _unknown(type(self).__name__, self.capability, "dimensiones inválidas")
        try:
            ar = round(width / height, 4)
            orientation = ("landscape" if width > height
                           else "portrait" if height > width else "square")
            margins = self._black_margins(frame.path)
            facts = {
                "width": width, "height": height, "aspect_ratio": ar,
                "orientation": orientation,
                "letterbox": margins["top"] > 0.02 and margins["bottom"] > 0.02,
                "pillarbox": margins["left"] > 0.02 and margins["right"] > 0.02,
                "black_margins": margins,
            }
            return _obs(type(self).__name__, self.capability, value=orientation, facts=facts)
        except Exception:
            return _unknown(type(self).__name__, self.capability, "error de cálculo")

    @staticmethod
    def _black_margins(path: str, black: int = 18) -> dict:
        img = _load(path, _WORK)
        if img is None:
            return {"top": 0.0, "bottom": 0.0, "left": 0.0, "right": 0.0}
        gray = img.convert("L")
        w, h = gray.size
        data = list(gray.getdata())

        def row_black(y):
            return all(data[y * w + x] <= black for x in range(w))

        def col_black(x):
            return all(data[y * w + x] <= black for y in range(h))

        top = next((y for y in range(h) if not row_black(y)), h)
        bottom = next((y for y in range(h) if not row_black(h - 1 - y)), h)
        left = next((x for x in range(w) if not col_black(x)), w)
        right = next((x for x in range(w) if not col_black(w - 1 - x)), w)
        return {"top": round(top / h, 4), "bottom": round(bottom / h, 4),
                "left": round(left / w, 4), "right": round(right / w, 4)}


def classical_detectors() -> list:
    """Detectores de visión clásica (VUE-002), en orden estable."""
    return [CompositionDetector(), ColorAnalysisDetector(), EdgeDensityDetector(),
            MotionEnergyDetector(), FrameGeometryDetector()]
