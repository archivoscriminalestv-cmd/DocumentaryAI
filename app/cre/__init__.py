"""Character Research Engine (CRE) — Sprint CRE-001.

Subsistema ADITIVO e independiente: transforma un personaje conocido en una
``CharacterBible`` estructurada (fuente de verdad), a partir de múltiples
proveedores de investigación (provider-agnostic). NO genera imágenes ni prompts,
NO mantiene consistencia y NO modifica el pipeline de vídeo.

Pipeline:  CharacterRequest → ResearchOrchestrator → N providers → Normalizer →
CharacterBible (+ manifest + report).
"""

SCHEMA_VERSION = "1.0"
