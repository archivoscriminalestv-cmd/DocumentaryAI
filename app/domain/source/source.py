"""Source — origen del que procede la información de una Research.

WP-0025 OBJ-027 (Source). Toda Source pertenece a una Research (ADR-0001: toda
actividad ocurre dentro de una Research). ``reference`` identifica la fuente
(título/URI) y ``content`` es el material registrado en bruto.
"""

from dataclasses import dataclass


@dataclass
class Source:
    id: str
    research_id: str
    reference: str
    content: str
