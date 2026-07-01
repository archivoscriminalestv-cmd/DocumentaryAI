"""Production Context (PCX) — `app/pcx/`.

El **contrato arquitectónico permanente** y único punto de entrada de información para los
motores de GENERACIÓN (VIS, VAI, Composer, Narration, Music, futuros). A partir de aquí, los
generadores NO leen KBG ni knowledge/ ni conocen DLE/DKS/EAE/ECE…: solo conocen
``ProductionContext``.

Subsistema diminuto y desacoplado: NO decide nada; solo CONSTRUYE el contexto que la
generación consumirá. Determinista, provider-agnóstico, solo lectura, `UNKNOWN` antes que
inventar. Es la frontera entre Knowledge y Generation. No persiste nada (vive en memoria).
"""

SCHEMA_VERSION = "0.1"
PCX_VERSION = "PCX-001"
UNKNOWN = "UNKNOWN"
