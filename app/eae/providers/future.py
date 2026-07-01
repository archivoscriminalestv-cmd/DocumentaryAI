"""Proveedor de marcador para futuras fuentes (contrato). Punto de extensión.

Demuestra que añadir una fuente nueva = una clase ``EvidenceProvider`` más, sin tocar el
orquestador ni el resto del EAE. Sin red.
"""

from app.eae.providers.base import BaseEvidenceProvider


class FutureProvider(BaseEvidenceProvider):
    name = "future"
    kinds = ()
