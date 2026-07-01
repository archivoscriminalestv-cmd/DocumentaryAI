"""ProductionContextBuilder (PCX) — construye el ProductionContext, no decide nada.

Carga GenerationKnowledge (objeto, JSON o vía KBG), ignora las decisiones UNKNOWN y arma un
``ProductionContext`` determinista. Nunca inventa; tolera que no exista ningún artefacto (en
ese caso el contexto queda vacío y la generación se comporta exactamente igual que antes).
"""

from app.pcx import UNKNOWN
from app.pcx.loader import (
    decisions_from_generation_knowledge,
    genre_of,
    load_generation_knowledge,
)
from app.pcx.models import ProductionContext


class ProductionContextBuilder:
    def build(self, *, generation_knowledge=None, gk_json_path: str = "",
              styles_root: str = "", genre: str = "documentary_style",
              ece_coverage_path: str = "", **reserved) -> ProductionContext:
        gk = load_generation_knowledge(
            generation_knowledge=generation_knowledge, gk_json_path=gk_json_path,
            styles_root=styles_root, genre=genre, ece_coverage_path=ece_coverage_path)

        ctx = ProductionContext(genre=genre_of(gk, genre))
        ctx.generation = decisions_from_generation_knowledge(gk)

        # Campos reservados (futuros): se aceptan por composición sin romper contratos.
        for key in ("evidence_coverage", "recreation_policy", "project_constraints",
                    "target_platform", "duration", "audience", "language",
                    "case_metadata", "production_preferences", "user_preferences"):
            if key in reserved and reserved[key] is not None:
                setattr(ctx, key, reserved[key])
        return ctx

    def empty(self, genre: str = UNKNOWN) -> ProductionContext:
        return ProductionContext(genre=genre)
