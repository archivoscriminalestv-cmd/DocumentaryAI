"""Base de los proveedores de evidencia (contrato; sin red, sin implementación real)."""

from app.eae.interfaces import EvidenceQuery
from app.eae.models import Evidence, EvidenceReference


class BaseEvidenceProvider:
    """Implementa ``EvidenceProvider`` como CONTRATO: no descarga ni hace peticiones.

    ``available()`` es False (no implementado), ``search()`` devuelve [] y ``fetch()``
    lanza NotImplementedError. Las subclases reales (futuras) sobreescribirán esto sin
    cambiar la interfaz ni el orquestador.
    """

    name = "base"
    kinds: tuple = ()

    def available(self) -> bool:
        return False

    def search(self, query: EvidenceQuery) -> list[EvidenceReference]:
        return []  # contrato: aún no busca (sin red)

    def fetch(self, reference: EvidenceReference) -> Evidence:
        raise NotImplementedError(
            f"{self.name}: la adquisición real llegará en un sprint posterior")
