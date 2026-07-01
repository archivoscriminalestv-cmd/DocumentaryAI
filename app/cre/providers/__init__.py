"""Proveedores de investigación del CRE (provider-agnostic, plug-in)."""

from app.cre.providers.base import ResearchProvider, ResearchResult

__all__ = ["ResearchProvider", "ResearchResult"]
