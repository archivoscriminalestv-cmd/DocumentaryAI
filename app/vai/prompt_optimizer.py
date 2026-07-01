"""PromptOptimizer — combina la VisualSpecification en un prompt final.

Orden canónico (ARCH-VIS-000 §12): lenguaje de cámara + composición → sujeto →
atmósfera/entorno → lente → iluminación → color grade → realismo + calidad.
Deduplica (sin repeticiones, case-insensitive, preservando orden) y limpia.
Independiente de proveedor: produce texto neutro y bien ordenado.
"""

from app.vai.models import VisualContext, VisualSpecification


class PromptOptimizer:
    def optimize(self, spec: VisualSpecification, context: VisualContext) -> str:
        camera = list(spec.camera_language)
        lead = camera[0] if camera else "cinematic shot"
        rest_camera = camera[1:]

        ordered: list[str] = [f"{lead} of {spec.subject}"]
        ordered += rest_camera
        ordered += spec.composition
        ordered += spec.atmosphere
        ordered += spec.lens
        ordered += spec.lighting
        ordered += spec.color_grade
        ordered += spec.realism
        ordered += spec.quality

        return ", ".join(self._dedupe(ordered))

    @staticmethod
    def _dedupe(fragments: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for fragment in fragments:
            text = " ".join(str(fragment).split()).strip(" ,")
            if not text:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(text)
        return out
