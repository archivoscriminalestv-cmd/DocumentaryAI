"""Live Learning Monitor (DLE-003) — seguimiento en tiempo real del aprendizaje.

Subsistema **aditivo**. El monitor NUNCA inspecciona el estado interno del DLE/Queue:
solo escucha **eventos públicos de progreso** (``ProgressEvent``) emitidos por el
pipeline. Determinista y sin dependencias externas.

Mantener este ``__init__`` ligero (sin importar submódulos) para que el DLE/Queue
puedan importar ``app.dle.monitor.events`` sin arrastrar el renderizador.
"""

MONITOR_VERSION = "DLE-003"
