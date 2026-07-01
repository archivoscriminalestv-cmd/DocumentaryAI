"""Detectores de DISPOSICIÓN y LOCALIZACIÓN del VUE (VUE-003).

Visión clásica (Pillow + matemáticas + geometría). Describen la geometría OBJETIVA del
plano (dónde está la masa visual, equilibrio, peso, espacio vacío). NO clasifican el tipo
de plano ni reconocen objetos: eso vendrá después (Shot Size / Composition se construirán
sobre estos hechos). Deterministas; nunca lanzan; UNKNOWN cuando no se puede medir.
"""

from PIL import Image

from app.vue import UNKNOWN
from app.vue.cv_detectors import _METHOD, _edge_density, _load, _obs, _unknown
from app.vue.interfaces import FrameRef
from app.vue.models import EmptySpace, LayoutBalance, SubjectRegion, VisualWeight

_WORK = (128, 72)
_GRID = (12, 8)           # rejilla para espacio vacío
_SALIENCY_EDGE = 40
_EMPTY_CELL_EDGE = 0.03   # celda "vacía" si su densidad de bordes < esto


def _lum(path: str, size=_WORK):
    img = _load(path, size)
    if img is None:
        return None, 0, 0, None
    gray = img.convert("L")
    return list(gray.getdata()), gray.size[0], gray.size[1], gray


def _third(v: float) -> str:
    return "left" if v < 1 / 3 else "right" if v >= 2 / 3 else "center"


def _third_v(v: float) -> str:
    return "top" if v < 1 / 3 else "bottom" if v >= 2 / 3 else "middle"


# --- 1) Subject localization (región saliente por bordes/contraste) ----------

class SubjectLocalizationDetector:
    capability = "subject_localization"

    def detect(self, frame: FrameRef, context: dict | None = None):
        img = _load(frame.path, _WORK)
        if img is None:
            return _unknown(type(self).__name__, self.capability, "frame no legible")
        try:
            from PIL import ImageFilter
            gray = img.convert("L")
            w, h = gray.size
            edges = gray.filter(ImageFilter.FIND_EDGES)
            data = list(edges.getdata())
            xs, ys = [], []
            for i, p in enumerate(data):
                if p > _SALIENCY_EDGE:
                    xs.append(i % w)
                    ys.append(i // w)
            frac = len(xs) / (w * h)
            if frac < 0.005:          # nada destaca -> sin sujeto determinable
                return _unknown(type(self).__name__, self.capability,
                                "sin región saliente determinable")
            x0, x1 = min(xs) / (w - 1), max(xs) / (w - 1)
            y0, y1 = min(ys) / (h - 1), max(ys) / (h - 1)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            occupancy = round((x1 - x0) * (y1 - y0), 4)
            distances = {"left": round(x0, 4), "right": round(1 - x1, 4),
                         "top": round(y0, 4), "bottom": round(1 - y1, 4)}
            region = SubjectRegion(
                bbox={"x0": round(x0, 4), "y0": round(y0, 4), "x1": round(x1, 4), "y1": round(y1, 4)},
                center={"x": round(cx, 4), "y": round(cy, 4)}, occupancy=occupancy,
                distances=distances, free_margin=round(min(distances.values()), 4),
                position=f"{_third_v(cy)}-{_third(cx)}", method=_METHOD,
                note="región saliente por bordes/contraste (no reconocimiento de objetos)")
            return _obs(type(self).__name__, self.capability, value=UNKNOWN, facts=region.to_dict())
        except Exception:
            return _unknown(type(self).__name__, self.capability, "error de cálculo")


# --- 2) Layout balance -------------------------------------------------------

class LayoutBalanceDetector:
    capability = "layout_balance"

    def detect(self, frame: FrameRef, context: dict | None = None):
        data, w, h, gray = _lum(frame.path)
        if data is None:
            return _unknown(type(self).__name__, self.capability, "frame no legible")
        try:
            total = sum(data) or 1
            # distribución horizontal (tercios de columnas) y vertical (tercios de filas)
            hcol = [0.0, 0.0, 0.0]
            vrow = [0.0, 0.0, 0.0]
            cells = [0.0] * 9
            for i, p in enumerate(data):
                x, y = i % w, i // w
                hcol[min(2, x * 3 // w)] += p
                vrow[min(2, y * 3 // h)] += p
                cells[min(2, y * 3 // h) * 3 + min(2, x * 3 // w)] += p
            horizontal = {"left": round(hcol[0] / total, 4), "center": round(hcol[1] / total, 4),
                          "right": round(hcol[2] / total, 4)}
            vertical = {"top": round(vrow[0] / total, 4), "middle": round(vrow[1] / total, 4),
                        "bottom": round(vrow[2] / total, 4)}
            concentration = round(max(cells) / total, 4)
            dispersion = round(self._dispersion([c / total for c in cells]), 4)
            balance = LayoutBalance(
                horizontal=horizontal, vertical=vertical,
                horizontal_symmetry=self._symmetry(data, w, h, axis="h"),
                vertical_symmetry=self._symmetry(data, w, h, axis="v"),
                concentration=concentration, dispersion=dispersion)
            return _obs(type(self).__name__, self.capability, value=UNKNOWN, facts=balance.to_dict())
        except Exception:
            return _unknown(type(self).__name__, self.capability, "error de cálculo")

    @staticmethod
    def _symmetry(data, w, h, axis) -> float:
        diff = 0.0
        count = 0
        for i, p in enumerate(data):
            x, y = i % w, i // w
            if axis == "h":
                mirror = data[y * w + (w - 1 - x)]
            else:
                mirror = data[(h - 1 - y) * w + x]
            diff += abs(p - mirror)
            count += 1
        return round(1.0 - (diff / (count or 1)) / 255.0, 4)

    @staticmethod
    def _dispersion(fractions) -> float:
        import math
        nonzero = [f for f in fractions if f > 0]
        if len(nonzero) <= 1:
            return 0.0
        entropy = -sum(f * math.log(f) for f in nonzero)
        return entropy / math.log(len(fractions))   # 0..1 (1 = repartido uniforme)


# --- 3) Visual weight --------------------------------------------------------

class VisualWeightDetector:
    capability = "visual_weight"

    def detect(self, frame: FrameRef, context: dict | None = None):
        data, w, h, gray = _lum(frame.path)
        if data is None:
            return _unknown(type(self).__name__, self.capability, "frame no legible")
        try:
            total = sum(data) or 1
            left = top = sx = sy = 0.0
            for i, p in enumerate(data):
                x, y = i % w, i // w
                if x < w / 2:
                    left += p
                if y < h / 2:
                    top += p
                sx += p * x
                sy += p * y
            weight = VisualWeight(
                left=round(left / total, 4), right=round(1 - left / total, 4),
                top=round(top / total, 4), bottom=round(1 - top / total, 4),
                center_of_gravity={"x": round(sx / total / (w - 1), 4),
                                   "y": round(sy / total / (h - 1), 4)})
            return _obs(type(self).__name__, self.capability, value=UNKNOWN, facts=weight.to_dict())
        except Exception:
            return _unknown(type(self).__name__, self.capability, "error de cálculo")


# --- 4) Empty space ----------------------------------------------------------

class EmptySpaceDetector:
    capability = "empty_space"

    def detect(self, frame: FrameRef, context: dict | None = None):
        img = _load(frame.path, _WORK)
        if img is None:
            return _unknown(type(self).__name__, self.capability, "frame no legible")
        try:
            gray = img.convert("L")
            w, h = gray.size
            gx, gy = _GRID
            empty = [[False] * gx for _ in range(gy)]
            for cy in range(gy):
                for cx in range(gx):
                    cell = gray.crop((cx * w // gx, cy * h // gy,
                                      (cx + 1) * w // gx, (cy + 1) * h // gy))
                    empty[cy][cx] = _edge_density(cell) < _EMPTY_CELL_EDGE
            empty_cells = sum(r.count(True) for r in empty)
            empty_fraction = round(empty_cells / (gx * gy), 4)
            comp_cells, bbox = self._largest_region(empty, gx, gy)
            largest = EmptySpace(
                empty_fraction=empty_fraction,
                largest_empty_fraction=round(comp_cells / (gx * gy), 4),
                largest_empty_bbox=bbox,
                distribution=self._distribution(empty, gx, gy))
            return _obs(type(self).__name__, self.capability, value=UNKNOWN, facts=largest.to_dict())
        except Exception:
            return _unknown(type(self).__name__, self.capability, "error de cálculo")

    @staticmethod
    def _largest_region(empty, gx, gy):
        seen = [[False] * gx for _ in range(gy)]
        best, best_cells = None, 0
        for sy in range(gy):
            for sx in range(gx):
                if not empty[sy][sx] or seen[sy][sx]:
                    continue
                stack, cells = [(sy, sx)], []
                seen[sy][sx] = True
                while stack:
                    y, x = stack.pop()
                    cells.append((y, x))
                    for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                        if 0 <= ny < gy and 0 <= nx < gx and empty[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((ny, nx))
                if len(cells) > best_cells:
                    best_cells = len(cells)
                    ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
                    best = {"x0": round(min(xs) / gx, 4), "y0": round(min(ys) / gy, 4),
                            "x1": round((max(xs) + 1) / gx, 4), "y1": round((max(ys) + 1) / gy, 4)}
        return best_cells, best

    @staticmethod
    def _distribution(empty, gx, gy):
        thirds = {"left": 0, "center": 0, "right": 0, "top": 0, "middle": 0, "bottom": 0}
        for cy in range(gy):
            for cx in range(gx):
                if not empty[cy][cx]:
                    continue
                thirds[_third(cx / gx)] += 1
                thirds[_third_v(cy / gy)] += 1
        return thirds


def layout_detectors() -> list:
    """Detectores de disposición/localización (VUE-003), orden estable."""
    return [SubjectLocalizationDetector(), LayoutBalanceDetector(),
            VisualWeightDetector(), EmptySpaceDetector()]
