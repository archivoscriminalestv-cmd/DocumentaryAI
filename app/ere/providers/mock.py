"""MockEvidenceProvider (ERE) — proveedor determinista y offline.

NO inventa hechos. Emite únicamente el nodo del sujeto a partir del ``ProjectQuery``
(nombre canónico + alias) para que el grafo tenga al menos la entidad consultada.
Si el query trae ``location``/``date`` explícitos, los registra como metadatos del
nodo (origen 'request'), nunca como hechos verificados. Confianza baja.
"""

from app.ere.models import Entity, ProjectQuery, SourceRef
from app.ere.providers.base import EvidenceProvider, EvidenceResult

CONFIDENCE = 0.2


class MockEvidenceProvider(EvidenceProvider):
    name = "mock-evidence"

    def research(self, query: ProjectQuery) -> EvidenceResult:
        metadata: dict[str, str] = {}
        if query.location:
            metadata["query_location"] = query.location
        if query.date:
            metadata["query_date"] = query.date

        entity = Entity(
            id=query.subject_id(),
            type="character",
            canonical_name=query.name,
            aliases=list(query.aliases),
            sources=[SourceRef(provider=self.name, source="request-derived",
                               confidence=CONFIDENCE)],
            metadata=metadata,
        )
        return EvidenceResult(
            self.name, True, entities=[entity], confidence=CONFIDENCE,
            notes="Datos NO verificados (mock): solo el sujeto del request.",
        )
