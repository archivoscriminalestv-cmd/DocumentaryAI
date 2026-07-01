"""CardImageRenderer — genera tarjetas de texto 16:9 con Pillow.

Render local determinista (sin IA ni red): cada escena se dibuja como una
tarjeta tipográfica sobre fondo oscuro. Es el seam ``ImageRenderer``: una
generación de imágenes por IA podrá sustituir este adaptador sin tocar el
pipeline. Encapsula la dependencia de Pillow (ARCH-0002 AP-006).
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

_WIDTH = 1280
_HEIGHT = 720
_BG = (17, 19, 26)
_FG = (236, 238, 242)
_ACCENT = (120, 170, 255)
_MARGIN = 96


class CardImageRenderer:
    def __init__(self, width: int = _WIDTH, height: int = _HEIGHT) -> None:
        self._width = width
        self._height = height

    def render(self, text: str, out_path: str, *, subtitle: str = "") -> bool:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

            image = Image.new("RGB", (self._width, self._height), _BG)
            draw = ImageDraw.Draw(image)

            body_font = self._font(40)
            subtitle_font = self._font(26)

            wrapped = self._wrap(text, draw, body_font, self._width - 2 * _MARGIN)
            self._draw_centered_block(draw, wrapped, body_font, _FG)

            if subtitle:
                draw.text(
                    (_MARGIN, self._height - 60),
                    subtitle,
                    font=subtitle_font,
                    fill=_ACCENT,
                )

            image.save(out_path, "PNG")
            return os.path.exists(out_path) and os.path.getsize(out_path) > 0
        except Exception:
            return False

    @staticmethod
    def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        for name in ("arial.ttf", "DejaVuSans.ttf", "segoeui.ttf"):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    def _wrap(self, text, draw, font, max_width: int) -> list[str]:
        # Ajuste por anchura real usando un nº de columnas aproximado y midiendo.
        avg_char = max(1, draw.textlength("x", font=font))
        columns = max(10, int(max_width / avg_char))
        lines: list[str] = []
        for paragraph in text.split("\n"):
            lines.extend(textwrap.wrap(paragraph, width=columns) or [""])
        return lines[:12]  # límite defensivo para no desbordar la tarjeta

    def _draw_centered_block(self, draw, lines: list[str], font, fill) -> None:
        line_height = font.size + 14 if hasattr(font, "size") else 34
        total = line_height * len(lines)
        y = max(_MARGIN, (self._height - total) // 2)
        for line in lines:
            line_width = draw.textlength(line, font=font)
            x = (self._width - line_width) // 2
            draw.text((x, y), line, font=font, fill=fill)
            y += line_height
