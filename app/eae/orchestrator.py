"""EvidenceAcquisitionEngine — coordina el EAE (EAE-001).

SOLO coordina: providers → verification → deduplication → storage. No implementa lógica
ni hace peticiones reales. En este sprint produce un ``EvidenceCase`` (vacío, con la
trazabilidad de qué proveedores se consultaron), demostrando la arquitectura.
"""

import logging

from app.eae import NOT_IMPLEMENTED
from app.eae.deduplication import BaseEvidenceDeduplicator
from app.eae.interfaces import EvidenceQuery
from app.eae.models import EvidenceCase
from app.eae.providers import default_providers
from app.eae.storage import BaseEvidenceStorage
from app.eae.verification import BaseEvidenceVerifier


class EvidenceAcquisitionEngine:
    def __init__(self, *, providers=None, verifier=None, deduplicator=None, storage=None,
                 logger=None) -> None:
        self.providers = list(providers) if providers is not None else default_providers()
        self.verifier = verifier or BaseEvidenceVerifier()
        self.deduplicator = deduplicator or BaseEvidenceDeduplicator()
        self.storage = storage or BaseEvidenceStorage()
        self._log = logger or logging.getLogger("eae")

    def acquire(self, query: EvidenceQuery) -> EvidenceCase:
        """Coordina la adquisición. EAE-001: contrato (sin descarga real)."""
        case = EvidenceCase(case_id=query.case_id, title=query.subject)
        consulted = []
        for provider in self.providers:
            try:
                references = provider.search(query)   # contrato: [] por ahora
            except Exception as exc:  # noqa: BLE001 — un proveedor no rompe la coordinación
                self._log.warning("EAE provider '%s' falló: %s", getattr(provider, "name", "?"), exc)
                references = []
            consulted.append(getattr(provider, "name", type(provider).__name__))
            # En sprints futuros: fetch → verify → dedup → store por cada referencia.
        case.notes = [
            "EAE-001: solo arquitectura; sin descarga/peticiones reales.",
            f"Proveedores consultados (contrato): {', '.join(consulted)}.",
            f"Verificación/deduplicación/almacenamiento: {NOT_IMPLEMENTED} (contratos listos).",
        ]
        return case

    def storage_layout(self) -> dict:
        return self.storage.layout()
