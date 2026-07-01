"""DocumentaryAI Chief Architect (DCA) — `app/dca/`.

El arquitecto PERMANENTE de DocumentaryAI: comprende toda la arquitectura (motores,
dominios, capacidades, dependencias, pipeline, documentación) y la expone como un modelo
consultable — el "gemelo digital" del sistema.

NO es un motor de generación: no analiza vídeos, no aprende, no descarga, no llama a IA,
no genera imágenes, no ejecuta el pipeline y NO modifica ningún subsistema. Solo lectura,
determinista, mediante contratos públicos. ``UNKNOWN`` antes que inventar. Escribe solo en
``output/dca/`` (nunca en ``knowledge/``).
"""

SCHEMA_VERSION = "0.1"
DCA_VERSION = "DCA-001"
UNKNOWN = "UNKNOWN"
