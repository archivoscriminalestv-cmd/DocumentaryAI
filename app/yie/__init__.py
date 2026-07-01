"""YouTube Intelligence Engine (YIE) — `app/yie/`.

Subsistema **aditivo, independiente, provider-agnóstico y determinista** que analiza
una URL de YouTube ANTES del DLE y almacena conocimiento permanente sobre el vídeo, el
canal, el SEO, la miniatura y la popularidad. Objetivo: aprender *por qué* funcionan los
documentales en YouTube (inteligencia competitiva), sin tocar el pipeline de generación.

Principios (igual que el DLE): NUNCA inventa (``UNKNOWN`` antes que inventar), sin IA ni
modelos externos, sin heurísticas específicas de ningún nicho, sin puntuaciones
arbitrarias. Misma URL → mismos JSON (las métricas dependientes del tiempo usan una
``reference_date`` explícita e inyectable).
"""

SCHEMA_VERSION = "1.0"
YIE_VERSION = "YIE-001"
UNKNOWN = "UNKNOWN"
