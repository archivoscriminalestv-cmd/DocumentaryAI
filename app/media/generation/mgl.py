"""MediaGenerationLayer (MGL) — orquestador de generación de media.

Flujo:  Scene → prompt → [Reuse Engine] → Provider Router → Asset → Store → Asset

- Convierte una Scene en prompt (usa ``image_prompt`` si existe; si no, title +
  narration).
- ANTES de generar, consulta el ``ReuseEngine``: si existe un asset suficientemente
  similar (score >= umbral), lo REUTILIZA (registra la nueva escena e incrementa
  ``reuse_count``) en lugar de generar uno nuevo.
- Si no hay match, pide el asset al ``ProviderRouter`` (con fallback) y lo persiste
  en el ``AssetStore``.

NO modifica los providers ni el pipeline de vídeo (FFmpeg). Devuelve un Asset cuyo
``path`` puede consumir el compositor.
"""

import logging

from app.media.generation.provider_router import ProviderRouter, default_router
from app.media.reuse.reuse_engine import ReuseEngine
from app.media.store.asset_store import AssetStore
from app.media.store.models import Asset
from app.media.styles.style_engine import StyleEngine

logger = logging.getLogger(__name__)


class MediaGenerationLayer:
    def __init__(
        self,
        router: ProviderRouter | None = None,
        store: AssetStore | None = None,
        reuse_engine: ReuseEngine | None = None,
        *,
        reuse_threshold: float = 0.75,
        style_engine: StyleEngine | None = None,
        style: str | None = None,
    ) -> None:
        self._store = store or AssetStore()
        self._router = router or default_router(self._store.base_dir)
        self._reuse = reuse_engine or ReuseEngine(reuse_threshold)
        self._reuse_threshold = reuse_threshold
        # Style & Prompt Intelligence (Fase A): opcional y aditivo. Si se fija un
        # ``style``, todas las escenas de este MGL (= un vídeo) lo comparten
        # (Visual Consistency Lock). Sin estilo, el comportamiento es el previo.
        self._style = style
        self._style_engine = style_engine or (StyleEngine() if style else None)

    @staticmethod
    def scene_to_prompt(scene) -> str:
        prompt = str(getattr(scene, "image_prompt", "") or "")
        if not prompt:
            title = str(getattr(scene, "title", ""))
            narration = str(getattr(scene, "narration", ""))
            prompt = f"{title}. {narration}".strip(". ").strip()
        return " ".join(prompt.split())

    def generate_for_scene(self, scene, media_type: str = "image") -> Asset:
        if self._style_engine is not None and self._style:
            prompt = self._style_engine.enrich_prompt(scene, self._style)
        else:
            prompt = self.scene_to_prompt(scene)
        scene_id = str(getattr(scene, "id", "") or getattr(scene, "scene_id", ""))
        style_tags = list(getattr(scene, "style_tags", []) or [])
        scene_type = getattr(scene, "scene_type", None)

        # 1) Reutilización: si hay un asset similar del mismo tipo, lo devolvemos.
        match = self._reuse.find_best_match(
            prompt,
            self._store,
            media_type=media_type,
            threshold=self._reuse_threshold,
            scene_type=scene_type,
            style_tags=style_tags,
        )
        if match is not None:
            self._store.register_reuse(match.asset_id, scene_id)
            reused = self._store.get(match.asset_id)
            logger.info(
                "REUSE asset=%s type=%s scene=%s reuse_count=%d (sin generar)",
                reused.asset_id, media_type, scene_id, reused.reuse_count,
            )
            return reused

        # 2) Generación vía router (con fallback) + persistencia.
        asset = self._router.generate(prompt, media_type=media_type)
        asset.scene_id = scene_id
        self._store.add(asset)
        logger.info(
            "GENERATE asset=%s type=%s scene=%s provider=%s",
            asset.asset_id, media_type, scene_id, asset.provider,
        )
        return asset

    def generate_for_shot(self, request) -> Asset:
        """Ejecuta un ShotRequest de VIS-2 (contrato VIS→MGL, aditivo).

        Reutiliza SOLO si ``reuse_key`` no está vacío y el ReuseEngine encuentra
        coincidencia (motivo recurrente). Con ``reuse_key`` vacío genera SIEMPRE
        un asset nuevo -> unicidad garantizada (elimina el colapso por reuse). No
        modifica providers ni el ReuseEngine: solo decide cuándo consultarlo.
        """
        prompt = str(getattr(request, "prompt", ""))
        media_type = str(getattr(request, "media_type", "image"))
        scene_id = str(getattr(request, "scene_id", ""))
        reuse_key = str(getattr(request, "reuse_key", "") or "")

        # Reutilización SOLO por motivo explícito (reuse_key). Se indexa por
        # ``style_tags`` (campo existente del Asset) -> no toca el ReuseEngine.
        if reuse_key:
            for existing in self._store.all():
                if existing.type == media_type and reuse_key in (existing.style_tags or []):
                    self._store.register_reuse(existing.asset_id, scene_id)
                    logger.info("REUSE(shot) asset=%s motif=%s scene=%s", existing.asset_id, reuse_key, scene_id)
                    return self._store.get(existing.asset_id)

        asset = self._router.generate(prompt, media_type=media_type)
        asset.scene_id = scene_id
        if reuse_key:
            asset.style_tags = list(asset.style_tags or []) + [reuse_key]
        self._store.add(asset)
        logger.info(
            "GENERATE(shot) asset=%s type=%s scene=%s provider=%s unique=%s",
            asset.asset_id, media_type, scene_id, asset.provider, not reuse_key,
        )
        return asset
