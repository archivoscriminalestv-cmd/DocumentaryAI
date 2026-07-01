"""Documentary Dossier — `app/dossier/`.

Subsistema **aditivo** e independiente que consume el ``EvidenceGraph`` del ERE y
produce un único ``DocumentaryDossier``: la fuente oficial de verdad de DocumentaryAI.

Solo información pública y verificable. NUNCA inferencias, opiniones, IA, resúmenes,
narrativa, prompts ni decisiones sobre qué es importante (eso será trabajo posterior
del Director IA). Cada afirmación conserva ``confidence``, ``provider``, ``source_url``
y ``license``. No modifica CRE/VIS/VAI/VSC/VPL/Motion/Composer/FFmpeg.
"""

SCHEMA_VERSION = "1.0"
DOSSIER_VERSION = "ERE-003"
