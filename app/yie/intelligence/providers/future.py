"""Contratos de proveedores FUTUROS (YIE-002) — interfaces preparadas, no implementadas.

SocialBlade, Google Trends, Wayback Machine y TubeBuddy. Cumplen el contrato
``EnrichmentProvider`` pero hoy NO están disponibles (``available()`` False, ``fetch``
devuelve ``{}``). Activarlos en el futuro será aportar un ``client`` oficial sin tocar el
orquestador ni el resto del sistema. Solo datos públicos; nunca navegador ni HTML.
"""


class _UnavailableEnrichment:
    name = "unavailable"

    def __init__(self, client=None) -> None:
        self._client = client

    def available(self) -> bool:
        return False

    def fetch(self, video_id: str, raw: dict) -> dict:
        return {}


class SocialBladeProvider(_UnavailableEnrichment):
    name = "socialblade"


class GoogleTrendsProvider(_UnavailableEnrichment):
    name = "google-trends"


class WaybackProvider(_UnavailableEnrichment):
    name = "wayback"


class TubeBuddyProvider(_UnavailableEnrichment):
    name = "tubebuddy"
