"""ReferenceDocumentaryAnalyzer (RDA) — fachada del motor de análisis.

Motor NO ligado a un vídeo concreto: analiza cualquier referencia accesible
(fichero local o URL) y extrae SOLO su gramática audiovisual como
``CinematicProfile`` (conocimiento reutilizable). No copia ni interpreta el
relato: ni transcripción, ni objetos, ni narrativa.

Flujo:  referencia → resolver fuente → extraer rasgos de fotograma → detectar
cortes → construir perfil → (opcional) guardar en la biblioteca.
"""

from app.rda.analysis import CUT_THRESHOLD, build_profile
from app.rda.frame_extractor import FfmpegFrameExtractor
from app.rda.library import ReferenceLibrary
from app.rda.models import CinematicProfile
from app.rda.sources import resolve_source


class ReferenceDocumentaryAnalyzer:
    def __init__(
        self,
        extractor: FfmpegFrameExtractor | None = None,
        library: ReferenceLibrary | None = None,
        *,
        sample_fps: float = 4.0,
        threshold: float = CUT_THRESHOLD,
    ) -> None:
        self._extractor = extractor or FfmpegFrameExtractor(sample_fps=sample_fps)
        self._library = library
        self._threshold = threshold

    def analyze(self, reference: str, *, persist: bool = True) -> CinematicProfile:
        path, source_type, cleanup = resolve_source(reference)
        try:
            meta = self._extractor.probe(path)
            frames = self._extractor.extract(path)
        finally:
            cleanup()  # borra cualquier descarga temporal (no se retiene contenido)

        if not frames:
            raise RuntimeError(f"No se pudieron extraer fotogramas de: {reference}")

        profile = build_profile(
            reference=reference,
            source_type=source_type,
            frames=frames,
            sample_fps=self._extractor.sample_fps,
            meta=meta,
            threshold=self._threshold,
        )
        if persist and self._library is not None:
            self._library.save(profile)
        return profile
