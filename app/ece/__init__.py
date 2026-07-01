"""Evidence Correlation Engine (ECE) — `app/ece/`.

Hace que DocumentaryAI deje de pensar en archivos aislados y empiece a razonar como un
investigador documental: correlaciona las evidencias mediante hechos OBSERVABLES en un
``EvidenceGraph`` tipado, analiza la cobertura documental por dimensiones, registra los
conflictos (sin decidir) y detecta dónde podrían hacer falta recreaciones — sin generarlas.

Solo análisis. NO genera imágenes/vídeos, NO llama a modelos, NO infiere relaciones sin
evidencia. La evidencia real tiene prioridad absoluta; la IA solo complementaría huecos.
Determinista. No toca DLE/YIE/VUE/VIS/VAI/Composer.
"""

SCHEMA_VERSION = "0.1"
ECE_VERSION = "ECE-001"
