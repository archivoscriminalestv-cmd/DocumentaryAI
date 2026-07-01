"""SceneGraphService — KnowledgeRelation[] -> Scene[] por travesía de grafo (C-07).

Generación de narrativa BASADA EN GRAFO, determinista y sin IA:

- Grafo: nodos = hechos (fact_ids), aristas = KnowledgeRelations.
- Cada Scene = un SUBGRAFO CONEXO (relaciones que comparten hechos, de forma
  transitiva) -> agrupa varias relaciones en una unidad narrativa; nunca una
  Scene por relación salvo que sea inevitable (relación aislada).
- Orden narrativo entre escenas: causal -> temporal -> jerárquico ->
  geográfico -> asociativo (las cadenas causales abren el documental).
- ``Scene.fact_ids`` = unión de los fact_ids de las relaciones del subgrafo
  (trazabilidad estricta; cero hechos inventados).
- ``title`` describe la RELACIÓN (cadena causal / cronología / contexto…),
  anclada en el término más frecuente del subgrafo (presente en los hechos).
- ``narration`` = prosa documental compuesta a partir del texto VERBATIM de las
  relaciones, enlazado con conectores según el tipo (sin listas, sin invención).

Reutiliza el ``Scene`` existente (app/domain/narrative). LÍMITE: la redacción
verdaderamente fluida (estilo locutor) corresponde a la capa de IA; aquí es
determinista y trazable.
"""

import re

from app.domain.narrative.scene import Scene

_PRIORITY = {
    "causal": 0,
    "temporal": 1,
    "hierarchical": 2,
    "geographical": 3,
    "associative": 4,
}

_TITLE = {
    "causal": "The causal chain behind {key}",
    "temporal": "The timeline of {key}",
    "hierarchical": "How {key} fits into the bigger picture",
    "geographical": "The setting that connects {key}",
    "associative": "The connections around {key}",
}
_TITLE_FALLBACK = {
    "causal": "How these events are causally connected",
    "temporal": "The sequence of related events",
    "hierarchical": "How these elements fit together",
    "geographical": "The shared setting of these events",
    "associative": "The connections between these facts",
}
_CONNECTIVE = {
    "causal": "As a consequence,",
    "temporal": "Subsequently,",
    "hierarchical": "More broadly,",
    "geographical": "In the same setting,",
    "associative": "Relatedly,",
}

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "at", "to", "and", "or", "is", "was",
    "were", "are", "be", "been", "it", "its", "that", "this", "these", "those",
    "for", "with", "as", "by", "from", "into", "near", "over", "after", "before",
    "had", "has", "have", "very", "their", "they", "which", "led", "occurred",
}


def _prio(rel_type) -> int:
    return _PRIORITY.get(str(rel_type), 5)


def _clean_parts(statement: str) -> list[str]:
    s = str(statement or "").strip()
    if s.startswith("[") and "] " in s:  # formato C-06: "[connector] A | B"
        s = s.split("] ", 1)[1]
    return [p.strip() for p in s.split(" | ") if p.strip()]


class _UnionFind:
    def __init__(self) -> None:
        self._parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self._parent.setdefault(x, x)
        root = x
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[x] != root:
            self._parent[x], x = root, self._parent[x]
        return root

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self._parent[rb] = ra


class SceneGraphService:
    def build(self, relations: list) -> list[Scene]:
        valid = [r for r in (relations or []) if self._is_valid(r)]
        if not valid:
            return []

        # 1) Construir componentes conexos sobre los nodos-hecho.
        uf = _UnionFind()
        for rel in valid:
            ids = [str(fid) for fid in rel.fact_ids]
            for fid in ids[1:]:
                uf.union(ids[0], fid)

        # 2) Agrupar relaciones por componente (orden de aparición = determinista).
        groups: dict[str, list] = {}
        for rel in valid:
            root = uf.find(str(rel.fact_ids[0]))
            groups.setdefault(root, []).append(rel)

        # 3) Ordenar componentes por flujo narrativo (tipo dominante), estable.
        ordered = sorted(
            enumerate(groups.values()),
            key=lambda pair: (min(_prio(r.relationship_type) for r in pair[1]), pair[0]),
        )

        scenes: list[Scene] = []
        for index, (_, component) in enumerate(ordered, start=1):
            scenes.append(self._compose_scene(f"scene-{index:02d}", component))
        return scenes

    @staticmethod
    def _is_valid(rel) -> bool:
        fact_ids = getattr(rel, "fact_ids", None)
        return (
            bool(fact_ids)
            and isinstance(fact_ids, (list, tuple))
            and getattr(rel, "relationship_type", None) is not None
        )

    def _compose_scene(self, scene_id: str, component: list) -> Scene:
        # Relaciones ordenadas dentro de la escena: causal primero, etc.
        ordered = sorted(
            enumerate(component), key=lambda p: (_prio(p[1].relationship_type), p[0])
        )
        ordered_rels = [rel for _, rel in ordered]
        dominant = str(ordered_rels[0].relationship_type)

        fact_ids: list[str] = []
        for rel in ordered_rels:
            for fid in rel.fact_ids:
                fid = str(fid)
                if fid not in fact_ids:
                    fact_ids.append(fid)

        return Scene(
            id=scene_id,
            title=self._title(dominant, ordered_rels),
            narration=self._narration(ordered_rels),
            fact_ids=fact_ids,
        )

    @staticmethod
    def _key(relations: list) -> str:
        counts: dict[str, int] = {}
        for rel in relations:
            for tok in _WORD.findall(str(getattr(rel, "statement", "")).lower()):
                if len(tok) >= 3 and tok not in _STOPWORDS:
                    counts[tok] = counts.get(tok, 0) + 1
        if not counts:
            return ""
        top = max(counts.values())
        return sorted(t for t, c in counts.items() if c == top)[0]

    def _title(self, dominant: str, relations: list) -> str:
        key = self._key(relations)
        if not key:
            return _TITLE_FALLBACK.get(dominant, _TITLE_FALLBACK["associative"])
        template = _TITLE.get(dominant, _TITLE["associative"])
        return template.format(key=key)

    @staticmethod
    def _narration(relations: list) -> str:
        sentences: list[str] = []
        for rel in relations:
            parts = [p.rstrip(" .") for p in _clean_parts(getattr(rel, "statement", ""))]
            parts = [p for p in parts if p]
            if not parts:
                continue
            connective = _CONNECTIVE.get(str(rel.relationship_type), "Relatedly,")
            sentence = parts[0] + "."
            for part in parts[1:]:
                sentence += f" {connective} {part}."
            sentences.append(sentence)
        return " ".join(sentences)
