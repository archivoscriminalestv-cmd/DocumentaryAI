"""Documentary Knowledge Synthesizer (DKS) — `app/dks/`.

Subsistema **aditivo** que LEE toda la base de conocimiento generada por el DLE
(``knowledge/documentaries/``) y SINTETIZA patrones de estilo en ``knowledge/styles/``.

NO descarga ni analiza vídeos. NO infiere: solo agrega (medias, medianas, histogramas,
distribuciones, correlaciones). Reproducible, versionado y provider-agnóstico. No toca
VIS/VAI ni la generación.
"""

SCHEMA_VERSION = "1.0"
DKS_VERSION = "DKS-001"
