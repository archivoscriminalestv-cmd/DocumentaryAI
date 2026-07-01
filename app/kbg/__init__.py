"""Knowledge Bridge (KBG) — `app/kbg/`.

La FRONTERA entre **Learning** y **Generation**: convierte el conocimiento aprendido por
DocumentaryAI (estilos del DKS, corpus, inteligencia de YouTube, advisor, ECE…) en
**decisiones objetivas de generación** (``GenerationKnowledge``).

NO crea contenido, NO analiza vídeos, NO aprende, NO ejecuta IA, NO genera prompts ni
imágenes y NO decide estética subjetiva. Solo traduce conocimiento en parámetros, por
composición y solo lectura. Determinista, provider-agnóstico. ``UNKNOWN`` antes que
inventar; cada decisión lleva origen, confianza, fuentes y motivo. Cierra el gap
``knowledge_unused`` detectado por el DCA. Escribe solo en ``output/kbg/``.
"""

SCHEMA_VERSION = "0.1"
KBG_VERSION = "KBG-001"
UNKNOWN = "UNKNOWN"
