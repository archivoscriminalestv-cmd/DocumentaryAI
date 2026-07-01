"""Research — unidad operacional del sistema.

ADR-0001: "La unidad operacional de DocumentaryAI es Research". Representa una
investigación delimitada en el tiempo y en el objetivo, cuya función es
transformar información externa en conocimiento reutilizable. No representa el
conocimiento permanente (eso es la Knowledge Base, ADR-0002).

ADR-0001 §3.2: una Research comienza y puede finalizar; el campo ``status``
refleja ese ciclo de forma mínima (provisional, pendiente de RFC-0002 para su
catálogo definitivo de estados).
"""

from dataclasses import dataclass


@dataclass
class Research:
    id: str
    title: str
    workspace_id: str | None = None
    status: str = "active"
