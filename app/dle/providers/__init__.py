"""Proveedores de origen de vídeo (provider-agnóstico: el origen no afecta al análisis)."""

from app.dle.providers.local_video import LocalVideoProvider
from app.dle.providers.youtube import YouTubeProvider

__all__ = ["LocalVideoProvider", "YouTubeProvider"]
