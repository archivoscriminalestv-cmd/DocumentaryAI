"""ProductionService: casos de uso de la fase de producción del documental.

Toma el conocimiento ya generado por ``ResearchService`` y lo transforma en los
artefactos que componen el vídeo final:

    Knowledge → Narrative → Voice → Images → Video

Esta primera iteración implementa la etapa Narrative de forma determinista (sin
IA externa): el guion se compone a partir de los hechos trazables del Knowledge.
La generación con LLM podrá sustituir ``_compose_segments`` más adelante sin
cambiar el resto del pipeline.
"""

import contextlib
import os
import tempfile
import wave
from uuid import uuid4

from app.application.ports import (
    FactRepository,
    ImageRenderer,
    KnowledgeRepository,
    NarrativeRepository,
    SpeechSynthesizer,
    VideoComposer,
)
from app.domain.fact import Fact
from app.domain.narrative import Narrative, NarrativeSegment
from app.domain.narrative.scene import Scene
from app.domain.video import Documentary, VideoScene
from app.domain.visual import Storyboard, VisualScene
from app.domain.voice import Voiceover, VoiceClip

# Segundos por palabra para estimar la duración de escenas sin audio real.
_SECONDS_PER_WORD = 0.4
_MIN_SCENE_SECONDS = 3.0

# Nº de escenas de cuerpo en las que se reparte el guion. Mantenerlo pequeño
# evita vídeos con cientos de microescenas y produce un ritmo documental.
_MAX_BODY_SEGMENTS = 5


def _new_id() -> str:
    return uuid4().hex[:12]


class ProductionService:
    def __init__(
        self,
        knowledge: KnowledgeRepository,
        facts: FactRepository,
        narratives: NarrativeRepository,
        synthesizer: SpeechSynthesizer | None = None,
        renderer: ImageRenderer | None = None,
        composer: VideoComposer | None = None,
        normalizer=None,
    ) -> None:
        self._knowledge = knowledge
        self._facts = facts
        self._narratives = narratives
        self._synthesizer = synthesizer
        self._renderer = renderer
        self._composer = composer
        self._normalizer = normalizer

    def generate_narrative(self, research_id: str, title: str | None = None) -> Narrative:
        """Compone un guion documental a partir del Knowledge de la Research."""
        knowledge_items = self._knowledge.list_by_research(research_id)
        if not knowledge_items:
            raise ValueError(
                f"No hay Knowledge para la Research {research_id}; "
                "genera conocimiento antes de la narrativa."
            )
        knowledge = knowledge_items[-1]
        facts = self._facts.list_by_ids(knowledge.fact_ids)

        narrative_title = title or f"Documental: {research_id}"
        segments = self._compose_segments(facts, narrative_title)

        narrative = Narrative(
            id=_new_id(),
            research_id=research_id,
            knowledge_id=knowledge.id,
            title=narrative_title,
            segments=segments,
        )
        self._narratives.add(narrative)
        return narrative

    def narrative_from_scenes(
        self,
        research_id: str,
        knowledge_id: str,
        title: str,
        scenes: list[Scene],
    ) -> Narrative:
        """Adapta las escenas del LLM al ``Narrative`` de producción (B-08).

        Cada ``Scene`` se mapea a un ``NarrativeSegment`` para que Voice/Images/
        Video —que ya consumen ``Narrative``— rendericen el guion de la IA sin
        tocar sus etapas. ``narration`` alimenta voz/imagen; ``title`` viaja en
        ``kind`` para que el subtítulo de la imagen muestre el título de escena.
        La trazabilidad ``fact_ids`` se preserva intacta.
        """
        segments = [
            NarrativeSegment(
                id=scene.id or _new_id(),
                kind=scene.title or "scene",
                text=scene.narration,
                fact_ids=list(scene.fact_ids),
            )
            for scene in scenes
        ]
        narrative = Narrative(
            id=_new_id(),
            research_id=research_id,
            knowledge_id=knowledge_id,
            title=title,
            segments=segments,
        )
        self._narratives.add(narrative)
        return narrative

    def _compose_segments(
        self, facts: list[Fact], title: str
    ) -> list[NarrativeSegment]:
        segments: list[NarrativeSegment] = []

        intro_text = (
            f"{title}. "
            "En este documental reconstruimos los hechos a partir de las "
            f"evidencias recopiladas: {len(facts)} hecho(s) verificable(s)."
        )
        segments.append(
            NarrativeSegment(id=_new_id(), kind="intro", text=intro_text, fact_ids=[])
        )

        for group in self._chunk(facts, _MAX_BODY_SEGMENTS):
            body_text = " ".join(self._clean(fact.text) for fact in group)
            segments.append(
                NarrativeSegment(
                    id=_new_id(),
                    kind="body",
                    text=body_text,
                    fact_ids=[fact.id for fact in group],
                )
            )

        outro_text = (
            "Estos son los hechos tal como las evidencias los sostienen. "
            "Cada afirmación de este documental es trazable hasta su fuente."
        )
        segments.append(
            NarrativeSegment(id=_new_id(), kind="outro", text=outro_text, fact_ids=[])
        )

        return segments

    def generate_voiceover(self, narrative: Narrative, output_dir: str) -> Voiceover:
        """Sintetiza un clip de audio por cada escena del guion.

        Si no hay sintetizador o falla, degrada escribiendo el texto de la
        escena en un ``.txt`` y marcando el clip como ``synthesized=False``; el
        pipeline continúa para no bloquear la producción del vídeo.
        """
        voice_dir = os.path.join(output_dir, "voice")
        os.makedirs(voice_dir, exist_ok=True)

        clips: list[VoiceClip] = []
        for index, segment in enumerate(narrative.segments):
            wav_path = os.path.join(voice_dir, f"segment_{index:03d}.wav")
            synthesized = False
            if self._synthesizer is not None:
                synthesized = self._synthesizer.synthesize(segment.text, wav_path)

            if synthesized:
                audio_path = wav_path
            else:
                audio_path = os.path.join(voice_dir, f"segment_{index:03d}.txt")
                with open(audio_path, "w", encoding="utf-8") as handle:
                    handle.write(segment.text)

            clips.append(
                VoiceClip(
                    segment_id=segment.id,
                    kind=segment.kind,
                    audio_path=audio_path,
                    synthesized=synthesized,
                )
            )

        return Voiceover(id=_new_id(), narrative_id=narrative.id, clips=clips)

    def generate_storyboard(self, narrative: Narrative, output_dir: str) -> Storyboard:
        """Genera una imagen por cada escena del guion.

        Requiere un ``ImageRenderer`` configurado. Si una imagen no puede
        generarse, la escena se marca ``rendered=False`` y el pipeline continúa.
        """
        if self._renderer is None:
            raise ValueError("ProductionService no tiene ImageRenderer configurado.")

        images_dir = os.path.join(output_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        scenes: list[VisualScene] = []
        for index, segment in enumerate(narrative.segments):
            image_path = os.path.join(images_dir, f"segment_{index:03d}.png")
            subtitle = f"{narrative.title} · {segment.kind}"
            rendered = self._renderer.render(
                segment.text, image_path, subtitle=subtitle
            )
            scenes.append(
                VisualScene(
                    segment_id=segment.id,
                    kind=segment.kind,
                    image_path=image_path,
                    rendered=rendered,
                )
            )

        return Storyboard(id=_new_id(), narrative_id=narrative.id, scenes=scenes)

    def generate_video(
        self,
        narrative: Narrative,
        storyboard: Storyboard,
        voiceover: Voiceover,
        output_dir: str,
    ) -> Documentary:
        """Ensambla el documental final alineando imágenes, audio y duración.

        Las tres colecciones están alineadas por índice (una entrada por escena
        del guion). La duración de cada escena la marca su audio real; si no hay
        audio, se estima a partir de la longitud del texto.
        """
        if self._composer is None or self._normalizer is None:
            raise ValueError(
                "ProductionService necesita VideoComposer y MediaNormalizer."
            )

        scenes: list[VideoScene] = []
        for segment, visual, clip in zip(
            narrative.segments, storyboard.scenes, voiceover.clips
        ):
            if clip.synthesized:
                audio_path: str | None = clip.audio_path
                duration = self._wav_duration(clip.audio_path)
            else:
                audio_path = None
                duration = self._estimate_duration(segment.text)
            scenes.append(
                VideoScene(
                    image_path=visual.image_path,
                    audio_path=audio_path,
                    duration=duration,
                )
            )

        os.makedirs(output_dir, exist_ok=True)
        video_path = os.path.join(output_dir, "documentary.mp4")

        # RAW -> MediaNormalizer -> compositor. FAIL-FAST: errores de FFmpeg se
        # propagan inmediatamente (sin captura).
        with tempfile.TemporaryDirectory() as clips_dir:
            clip_paths: list[str] = []
            for index, scene in enumerate(scenes):
                clip_path = os.path.join(clips_dir, f"clip_{index:03d}.mkv")
                self._normalizer.scene_clip(
                    scene.image_path, scene.audio_path, scene.duration, clip_path
                )
                clip_paths.append(clip_path)
            self._composer.compose(clip_paths, video_path)

        return Documentary(
            id=_new_id(),
            narrative_id=narrative.id,
            video_path=video_path,
            rendered=True,
        )

    @staticmethod
    def _wav_duration(path: str) -> float:
        try:
            with contextlib.closing(wave.open(path, "rb")) as handle:
                frames = handle.getnframes()
                rate = handle.getframerate()
                if rate:
                    return max(_MIN_SCENE_SECONDS, frames / float(rate))
        except Exception:
            pass
        return _MIN_SCENE_SECONDS

    @staticmethod
    def _estimate_duration(text: str) -> float:
        words = len(text.split())
        return max(_MIN_SCENE_SECONDS, words * _SECONDS_PER_WORD)

    @staticmethod
    def _clean(text: str) -> str:
        cleaned = " ".join(text.split())
        if cleaned and cleaned[-1] not in ".!?":
            cleaned += "."
        return cleaned

    @staticmethod
    def _chunk(items: list[Fact], max_chunks: int) -> list[list[Fact]]:
        """Reparte ``items`` en, como mucho, ``max_chunks`` grupos contiguos."""
        if not items:
            return []
        chunk_count = min(max_chunks, len(items))
        size = -(-len(items) // chunk_count)  # división entera hacia arriba
        return [items[i : i + size] for i in range(0, len(items), size)]
