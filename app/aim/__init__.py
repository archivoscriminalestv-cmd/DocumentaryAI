"""API Integration Manager (AIM) — `app/aim/`.

Único punto central de DocumentaryAI para TODAS las conexiones externas. A partir de aquí,
ningún motor habla directamente con una API: lo hace a través del AIM, que centraliza
registro de proveedores, interfaces (Protocols), credenciales, health checks, matriz de
capacidades y resolución proveedor principal → alternativo → deshabilitado.

Este sprint construye la INFRAESTRUCTURA (para conectar cualquier proveedor en minutos), no
integra todavía cada API. Composición, determinista, sin IA, sin acoplar proveedores
concretos a los motores. Sin llamadas reales salvo el Health Check opcional. Nunca imprime ni
persiste credenciales. No modifica ningún otro subsistema.
"""

SCHEMA_VERSION = "0.1"
AIM_VERSION = "AIM-001"
UNKNOWN = "UNKNOWN"
