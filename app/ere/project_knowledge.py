"""ProjectKnowledge — contexto documental de entrada del ERE (ERE-002).

Nunca investigamos solo un nombre ("Coquito"): investigamos un PROYECTO documental
con su contexto (persona real, lugares, fechas, palabras clave, género…). Este objeto
serializable es la entrada oficial del Evidence Query Builder y la referencia que usan
el Ranking y la Entity Resolution.
"""

import json
from dataclasses import asdict, dataclass, field
from typing import Any

from app.ere.models import ProjectQuery, slugify


@dataclass
class ProjectKnowledge:
    title: str = ""
    canonical_name: str = ""
    aliases: list[str] = field(default_factory=list)
    known_people: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    country: str = ""
    language: str = ""
    genre: str = ""
    keywords: list[str] = field(default_factory=list)
    documentary_type: str = ""
    notes: str = ""

    # --- derivados -----------------------------------------------------------
    def subject_name(self) -> str:
        """Nombre del sujeto principal (canonical_name si existe; si no, title)."""
        return self.canonical_name or self.title

    def to_query(self) -> ProjectQuery:
        """Deriva el ProjectQuery base que consumen los proveedores.

        Clave para la desambiguación: el sujeto pasa a ser el ``canonical_name``
        (p.ej. 'Jonathan Burgos'), y el ``title`` ('Coquito') queda como alias.
        """
        name = self.subject_name()
        aliases = list(self.aliases)
        if self.title and self.title != name and self.title not in aliases:
            aliases.insert(0, self.title)
        return ProjectQuery(
            name=name,
            location=", ".join(self.locations),
            date=self.dates[0] if self.dates else "",
            aliases=aliases,
            hints={
                k: v for k, v in {
                    "genre": self.genre,
                    "language": self.language,
                    "country": self.country,
                    "documentary_type": self.documentary_type,
                }.items() if v
            },
        )

    def slug(self) -> str:
        return slugify(self.subject_name() or self.title)

    # --- serialización -------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectKnowledge":
        valid = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in (data or {}).items() if k in valid})

    @classmethod
    def load(cls, path: str) -> "ProjectKnowledge":
        with open(path, encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, ensure_ascii=False, indent=2, sort_keys=True)
