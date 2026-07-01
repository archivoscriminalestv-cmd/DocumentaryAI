"""Case Discovery Engine (EAE-003).

Recibe un ``InvestigationPlan`` y produce un ``DiscoveryPlan``: responde DÓNDE puede
existir el material (fuentes candidatas por capacidad) y, cuando un proveedor está
disponible, QUÉ evidencias concretas existen — **sin descargar nada**.

Determinista, provider-agnóstico, sin IA, sin scraping (solo APIs oficiales / proveedores
definidos), ``UNKNOWN`` antes que inventar. No toca el DLE ni la generación.
"""

DISCOVERY_SCHEMA_VERSION = "0.1"
