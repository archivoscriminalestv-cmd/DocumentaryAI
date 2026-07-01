"""Fact: minimal factual layer derived from Evidence.

Sprint B-04 introduces Fact between Evidence and Knowledge. For now, each
Evidence generates exactly one Fact with the same text.
"""

from dataclasses import dataclass


@dataclass
class Fact:
    id: str
    evidence_id: str
    text: str
