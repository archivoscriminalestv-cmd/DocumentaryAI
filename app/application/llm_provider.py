"""LLMProvider — puerto del proveedor de lenguaje (Sprint B-06.1, refactor).

Abstracción que invierte la dependencia: el NarrativeEngine depende solo de
este protocolo, nunca de un proveedor concreto (Anthropic/OpenAI/Gemini). Las
implementaciones viven en ``app/infrastructure/llm/`` (ARCH-0002 AP-006).

Nota de contrato: se conserva ``complete(system, user)`` —en lugar de un único
``generate(prompt)``— para preservar exactamente el comportamiento actual
(mismo system prompt + mensaje de usuario), los artefactos (``prompt.md`` con
secciones System/User) y los tests existentes. La inversión de dependencia es
idéntica; solo cambia el nombre del puerto, no su semántica.
"""

from typing import Protocol


class LLMProvider(Protocol):
    def complete(self, system: str, user: str) -> str: ...
