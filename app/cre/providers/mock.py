"""MockResearchProvider — proveedor determinista y genérico (CRE).

Disponible offline y reproducible. NO inventa hechos sobre personas reales: emite
un ESQUELETO de Character Bible con la identidad provista por el request (nombre,
alias, pistas explícitas) y deja el resto como vacío/desconocido, marcando los
datos como no verificados. Los proveedores reales (Wikipedia/News/Archive)
rellenarán datos verificados sin cambiar esta interfaz.
"""

from app.cre.models import CharacterRequest, slugify
from app.cre.providers.base import ResearchProvider, ResearchResult


class MockResearchProvider(ResearchProvider):
    name = "mock-research"

    def research(self, request: CharacterRequest) -> ResearchResult:
        hints = request.hints or {}
        identity = {
            "id": slugify(request.name),
            "canonical_name": request.name,
            "aliases": list(request.aliases),
            # Solo se reflejan pistas EXPLÍCITAS del request; nada se inventa.
            "nationality": hints.get("nationality", ""),
            "birth_date": hints.get("birth_date", ""),
            "death_date": hints.get("death_date", ""),
            "occupation": hints.get("occupation", ""),
        }
        return ResearchResult(
            provider=self.name,
            available=True,
            data={"identity": identity},
            visual_references=[],
            sources=["mock-research:request-derived"],
            confidence=0.2,  # baja: dato no verificado, pierde frente a fuentes reales
            notes="Datos NO verificados (mock determinista): solo identidad del request.",
        )
