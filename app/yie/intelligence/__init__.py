"""Competitive Intelligence & Audience Analytics (YIE-002) — `app/yie/intelligence/`.

Amplía el YIE con inteligencia competitiva: análisis profundo de canal, audiencia,
engagement, SEO extendido y miniatura extendida, más una capa de **proveedores de
enriquecimiento opcionales** (vidIQ ahora; SocialBlade/Google Trends/Wayback/TubeBuddy
como contratos futuros). Cada proveedor es independiente y opcional: si falta, los
campos quedan ``UNKNOWN`` y el pipeline continúa.

Aditivo, determinista, sin IA/modelos/scoring/recomendaciones. Reutiliza las funciones
puras del YIE-001 (no las modifica) y escribe ficheros NUEVOS por documental, además de
un ``provider_coverage.json`` auditable. No toca el DLE ni el DKS.
"""

SCHEMA_VERSION = "1.0"
CI_VERSION = "YIE-002"
