"""Style Resolver (KBG) — selección/fusión determinista de los perfiles por género.

Para un género (p.ej. ``true_crime``) reúne el perfil del género + los patrones del DKS
(cinematography/editing/lighting/motion/documentary_style) y los expone de forma uniforme.
Precedencia determinista: el fichero de patrón dedicado manda; si falta, se cae a las
``distributions`` del perfil de género. Nunca inventa: si no hay dato, devuelve ``None``.
"""

from dataclasses import dataclass, field

_AREA_FILES = {
    "cinematography": "cinematography_patterns",
    "editing": "editing_patterns",
    "lighting": "lighting_patterns",
    "motion": "motion_patterns",
    "documentary_style": "documentary_style",
}


@dataclass
class ResolvedStyle:
    genre: str
    profiles: dict = field(default_factory=dict)   # area -> data
    sources: dict = field(default_factory=dict)    # area -> path
    genre_profile: dict | None = None
    genre_source: str = ""

    def dist(self, area: str, key: str, genre_key: str | None = None):
        """Devuelve ``(distribution_dict, source)`` o ``(None, "")``."""
        data = self.profiles.get(area)
        if isinstance(data, dict) and isinstance(data.get(key), dict):
            return data[key], self.sources.get(area, "")
        if genre_key and isinstance(self.genre_profile, dict):
            dists = self.genre_profile.get("distributions", {})
            if isinstance(dists.get(genre_key), dict):
                return dists[genre_key], self.genre_source
        return None, ""

    def summary(self, area: str, key: str):
        data = self.profiles.get(area)
        if isinstance(data, dict) and isinstance(data.get(key), dict):
            return data[key], self.sources.get(area, "")
        return None, ""

    def applied_sources(self) -> list[str]:
        srcs = sorted(set(self.sources.values()))
        if self.genre_source and self.genre_source not in srcs:
            srcs.append(self.genre_source)
        return srcs


class StyleResolver:
    def resolve(self, bundle, genre: str) -> ResolvedStyle:
        resolved = ResolvedStyle(genre=genre)
        for area, fname in _AREA_FILES.items():
            data = bundle.style(fname)
            if data is not None:
                resolved.profiles[area] = data
                resolved.sources[area] = bundle.source(fname)
        # perfil de género (p.ej. true_crime.json); fallback a documentary_style
        genre_profile = bundle.style(genre) or bundle.style("documentary_style")
        if genre_profile is not None:
            resolved.genre_profile = genre_profile
            resolved.genre_source = bundle.source(genre) or bundle.source("documentary_style")
        return resolved
