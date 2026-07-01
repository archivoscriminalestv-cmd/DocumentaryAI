"""KnowledgeBridge (KBG) — coordinación: conocimiento público → GenerationKnowledge.

Solo composición y solo lectura. No genera nada; responde "dado el conocimiento aprendido,
¿cómo debería generarse ESTE documental?" en forma de decisiones objetivas.
"""

import os

from app.kbg import decision_engine
from app.kbg.knowledge_loader import load_optional, load_styles
from app.kbg.models import GenerationKnowledge
from app.kbg.style_resolver import StyleResolver


class KnowledgeBridge:
    def __init__(self, styles_root: str = os.path.join("knowledge", "styles")) -> None:
        self.styles_root = styles_root

    def build(self, *, genre: str = "documentary_style",
              ece_coverage_path: str = "") -> GenerationKnowledge:
        bundle = load_styles(self.styles_root)
        load_optional(bundle, ece_coverage=ece_coverage_path)
        resolved = StyleResolver().resolve(bundle, genre)
        gk = decision_engine.build(resolved, genre,
                                   ece_coverage=bundle.extra.get("ece_coverage"))
        gk.summary["applied_sources"] = resolved.applied_sources()
        return gk
