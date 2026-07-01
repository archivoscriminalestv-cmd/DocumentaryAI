"""FinalRenderService — capa de render final (Sprint C-10).

Consume ``MediaStyledScene[]`` (de C-09) y produce un ``FinalRender`` con el
informe JSON (timings + cache hits). Reglas:

- voz consistente en todas las escenas (voice_id + model GLOBALES),
- caché primero: nunca regenera audio/imagen ya cacheados,
- ElevenLabs solo en cache miss,
- intro inyectada únicamente en la primera escena,
- render determinista.

NO modifica narration/estructura/estilo/fact_ids: solo renderiza.
"""

import os
import tempfile

import time

from app.domain.render import AudioAsset, FinalRender, ImageAsset, VideoSegment

_SECONDS_PER_WORD = 0.4
_MIN_SCENE_SECONDS = 3.0
# Estimación de coste de ElevenLabs (USD por 1k caracteres); solo orientativa.
_COST_PER_1K_CHARS_USD = 0.30


class FinalRenderService:
    def __init__(
        self,
        voice_cache,
        image_cache,
        composer=None,
        normalizer=None,
        *,
        voice_id: str,
        model: str,
        output_dir: str = os.path.join("output", "render"),
    ) -> None:
        self._voice_cache = voice_cache
        self._image_cache = image_cache
        self._composer = composer
        self._normalizer = normalizer
        self._voice_id = voice_id  # GLOBAL: misma voz en todas las escenas
        self._model = model
        self._output_dir = output_dir

    def render(self, scenes: list) -> FinalRender:
        start = time.perf_counter()

        audio_assets: list[AudioAsset] = []
        image_assets: list[ImageAsset] = []
        segments: list[VideoSegment] = []
        v_hits = v_misses = i_hits = i_misses = 0
        miss_chars = 0  # caracteres que sí incurren en API (cache miss)

        for scene in scenes or []:
            scene_id = str(getattr(scene, "id", ""))
            narration = str(getattr(scene, "narration", ""))
            image_prompt = str(getattr(scene, "image_prompt", ""))
            intro = getattr(scene, "intro", None)

            # Intro injection: solo la primera escena trae intro != None.
            if intro is not None:
                segments.append(
                    VideoSegment(
                        scene_id=scene_id,
                        kind="intro",
                        image_path=str(getattr(intro, "asset", "")),
                        audio_path=None,
                        duration=float(getattr(intro, "duration", 0.0)),
                    )
                )

            # Audio (cache-first; ElevenLabs solo en miss).
            audio_path, a_hit, a_synth = self._voice_cache.get_or_synthesize(
                narration=narration,
                voice_id=self._voice_id,
                model=self._model,
                scene_id=scene_id,
            )
            if a_hit:
                v_hits += 1
            else:
                v_misses += 1
                miss_chars += len(narration)
            audio_assets.append(AudioAsset(scene_id, audio_path, a_hit, a_synth))

            # Imagen (cache-first).
            image_path, i_hit, i_rend = self._image_cache.get_or_render(
                image_prompt=image_prompt, scene_id=scene_id
            )
            if i_hit:
                i_hits += 1
            else:
                i_misses += 1
            image_assets.append(ImageAsset(scene_id, image_path, i_hit, i_rend))

            duration = self._estimate_duration(narration)
            segments.append(
                VideoSegment(
                    scene_id=scene_id,
                    kind="scene",
                    image_path=image_path,
                    audio_path=audio_path if a_synth else None,
                    duration=duration,
                )
            )

        final_path, rendered = self._compose(segments)
        intro_asset = next(
            (s.image_path for s in segments if s.kind == "intro"), ""
        )
        intro_concatenated = bool(
            rendered and intro_asset and os.path.exists(intro_asset)
        )
        total_duration = round(sum(s.duration for s in segments), 2)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        cost = (miss_chars / 1000.0) * _COST_PER_1K_CHARS_USD

        report = {
            "final_video_path": final_path if rendered else "",
            "total_duration": total_duration,
            "voice_cache_hits": v_hits,
            "voice_cache_misses": v_misses,
            "image_cache_hits": i_hits,
            "image_cache_misses": i_misses,
            "elevenlabs_cost_estimate": f"~{miss_chars} chars (~${cost:.4f})",
            "render_time_ms": elapsed_ms,
            "intro_injected": any(s.kind == "intro" for s in segments),
            "intro_concatenated": intro_concatenated,
            "rendered": rendered,
        }
        return FinalRender(
            final_video_path=final_path if rendered else "",
            rendered=rendered,
            scenes_audio=audio_assets,
            scenes_images=image_assets,
            video_segments=segments,
            report=report,
        )

    def _compose(self, segments: list[VideoSegment]) -> tuple[str, bool]:
        final_path = os.path.join(self._output_dir, "final_video.mp4")
        if self._composer is None or self._normalizer is None:
            return final_path, False

        scene_segments = [s for s in segments if s.kind == "scene"]
        if not scene_segments:
            return final_path, False
        os.makedirs(self._output_dir, exist_ok=True)

        intro_seg = next((s for s in segments if s.kind == "intro"), None)

        # RAW -> MediaNormalizer -> compositor. FAIL-FAST: cualquier error de FFmpeg
        # se propaga (no se captura) para que el fallo sea inmediato y reproducible.
        with tempfile.TemporaryDirectory() as clips_dir:
            clip_paths: list[str] = []
            for index, segment in enumerate(scene_segments):
                clip = os.path.join(clips_dir, f"clip_{index:03d}.mkv")
                self._normalizer.scene_clip(
                    segment.image_path, segment.audio_path, segment.duration, clip
                )
                clip_paths.append(clip)

            intro_clip = None
            if intro_seg and os.path.exists(intro_seg.image_path):
                intro_clip = os.path.join(clips_dir, "intro.mkv")
                self._normalizer.intro_clip(intro_seg.image_path, intro_clip)

            self._composer.compose(clip_paths, final_path, intro_clip=intro_clip)

        return final_path, True

    @staticmethod
    def _estimate_duration(text: str) -> float:
        words = len(text.split())
        return max(_MIN_SCENE_SECONDS, words * _SECONDS_PER_WORD)
