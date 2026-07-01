"""Loader del Architectural Backlog (DCA-004).

Convierte el documento humano ``docs/roadmap/ARCHITECTURAL-BACKLOG.md`` en modelos internos.
Determinista, sin red, sin IA. No escribe nada: solo lee.

Convención del documento (legible y parseable):
    ## 2. Strategic Priorities
    ### P0 — ...
    #### <Título de la entrada>
    - **id:** `mi_id`
    - **status:** PLANNED
    - **hypothesis:** UNKNOWN        (solo en Hypotheses)
    - **related:** `a`, `b`
    <descripción libre / viñetas>
"""

import os
import re

from app.dca.backlog.models import ArchitecturalBacklog, BacklogEntry, EntryStatus, Section

_SECTION_KEYWORDS = [
    ("strategic priorities", Section.STRATEGIC_PRIORITIES),
    ("open ideas", Section.OPEN_IDEAS),
    ("hypotheses", Section.HYPOTHESES),
    ("technical debt", Section.TECHNICAL_DEBT),
    ("completed", Section.COMPLETED),
    ("vision", Section.VISION),
]
_META_RE = re.compile(r"^- \*\*(?P<key>[a-z_]+):\*\*\s*(?P<val>.*?)\s*$")
_PRIORITY_RE = re.compile(r"\bP[0-3]\b")


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return s or "x"


def _section_of(heading: str) -> str | None:
    low = heading.lower()
    for keyword, section in _SECTION_KEYWORDS:
        if keyword in low:
            return section
    return None


def _clean_list(val: str) -> list[str]:
    val = val.strip().strip("[]")
    parts = re.split(r"[,\s]+", val)
    return [p.strip().strip("`") for p in parts if p.strip().strip("`")]


class BacklogLoader:
    def load(self, path: str) -> ArchitecturalBacklog:
        with open(path, encoding="utf-8") as h:
            text = h.read()
        backlog = self.parse(text)
        backlog.source_path = path
        return backlog

    def parse(self, text: str) -> ArchitecturalBacklog:
        backlog = ArchitecturalBacklog()
        section: str | None = None
        priority = ""
        vision_lines: list[str] = []
        current: BacklogEntry | None = None
        raw: list[str] = []

        def finalize() -> None:
            if current is not None:
                self._apply(current, raw)
                backlog.entries.append(current)

        for line in text.splitlines():
            if line.startswith("## "):
                finalize(); current = None; raw = []
                section = _section_of(line[3:]); priority = ""
                continue
            if line.startswith("### ") and section == Section.STRATEGIC_PRIORITIES:
                finalize(); current = None; raw = []
                m = _PRIORITY_RE.search(line)
                priority = m.group(0) if m else ""
                continue
            if line.startswith("#### "):
                finalize(); raw = []
                title = line[5:].strip()
                current = BacklogEntry(id=_slug(title), title=title,
                                       section=section or Section.OPEN_IDEAS,
                                       priority=priority if section == Section.STRATEGIC_PRIORITIES else "")
                continue
            if current is not None:
                raw.append(line)
            elif section == Section.VISION:
                vision_lines.append(line)

        finalize()
        backlog.vision = "\n".join(vision_lines).strip()
        return backlog

    # ------------------------------------------------------------------
    @staticmethod
    def _apply(entry: BacklogEntry, raw: list[str]) -> None:
        desc_lines: list[str] = []
        for line in raw:
            m = _META_RE.match(line)
            if m:
                key, val = m.group("key"), m.group("val")
                if key == "id" and val:
                    entry.id = val.strip().strip("`")
                elif key == "status" and val:
                    entry.status = val.strip().upper()
                elif key == "priority" and val:
                    entry.priority = val.strip().upper()
                elif key == "hypothesis" and val:
                    entry.hypothesis_status = val.strip().upper()
                elif key == "related" and val:
                    entry.related = _clean_list(val)
                elif key == "description" and val:
                    entry.description = val.strip()
                continue
            if line.strip():
                desc_lines.append(line.strip())
        if not entry.description and desc_lines:
            # primer párrafo como descripción
            para: list[str] = []
            for d in desc_lines:
                para.append(d)
            entry.description = " ".join(para)
        # Las hipótesis sin estado de ciclo explícito empiezan como IDEA.
        if entry.section == Section.HYPOTHESES and entry.status not in EntryStatus.ALL:
            entry.status = EntryStatus.IDEA
