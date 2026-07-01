"""DocumentaryLearningEngine — orquesta el aprendizaje de un documental.

Pipeline: vídeo → metadatos → (audio) → transcripción → escenas/planos → análisis
cinematográfico → Documentary Knowledge → persistencia. Provider-agnóstico y
determinista. Si una etapa falla, registra el error y CONTINÚA (no rompe el pipeline).
"""

import logging
import os
from dataclasses import dataclass

from app.dle.analysis.cinematography import analyze_shot
from app.dle.ffmpeg import FFmpegProbe, cuts_to_shots
from app.dle.models import (
    AnalysisError,
    DocumentaryKnowledge,
    Metadata,
    ShotAnalysis,
    Transcript,
)
from app.dle.monitor.events import PROGRESS, STARTED, ProgressEvent
from app.dle.segmentation.scene_detector import build_narrative_blocks, group_into_scenes
from app.dle.storage.knowledge_store import KnowledgeStore
from app.dle.storage.statistics import build_statistics
from app.dle.storage_policy import build_storage_policy
from app.dle.transcription.whisper import NullTranscriber


@dataclass
class VideoSource:
    path: str
    source_type: str
    source_ref: str
    video_id: str


class DocumentaryLearningEngine:
    def __init__(self, *, probe: FFmpegProbe | None = None, transcriber=None,
                 store: KnowledgeStore | None = None,
                 youtube_provider=None, local_provider=None, logger=None,
                 scene_threshold: float = 0.27, storage_policy=None) -> None:
        self.probe = probe or FFmpegProbe()
        self.transcriber = transcriber or NullTranscriber()
        self.store = store or KnowledgeStore()
        self._youtube = youtube_provider
        self._local = local_provider
        self._log = logger or logging.getLogger("dle")
        self.scene_threshold = scene_threshold
        # Ciclo de vida del vídeo (DLE-002A): TEMPORARY por defecto (borra el vídeo).
        self.storage_policy = storage_policy or build_storage_policy()

    # ------------------------------------------------------------------ API

    def learn(self, *, youtube: str | None = None, video: str | None = None,
              force: bool = False, work_dir: str | None = None, on_stage=None,
              on_event=None) -> dict:
        """``on_stage(stage)`` (opcional, aditivo) recibe: downloading | analyzing |
        learning | storing. ``on_event(ProgressEvent)`` (opcional, aditivo) emite eventos
        públicos de progreso para el monitor. Ninguno altera el análisis: solo notifican."""
        emit = on_stage or (lambda _s: None)

        def event(kind, stage, **kw):
            if on_event is not None:
                on_event(ProgressEvent(kind=kind, stage=stage, **kw))

        errors: list[AnalysisError] = []
        # El workspace del vídeo lo gestiona la política de almacenamiento: el vídeo
        # descargado es temporal y se elimina al salir (TEMPORARY) o se archiva (ARCHIVE),
        # también ante un error. El conocimiento ya se ha guardado en knowledge/ antes.
        with self.storage_policy.workspace(youtube or video or "src", work_dir=work_dir) as work:
            emit("downloading")
            event(STARTED, "downloading")
            source = self._resolve_source(youtube, video, work, errors)
            if source is None:
                return {"status": "error", "errors": [e.to_dict() for e in errors]}

            if self.store.exists(source.video_id) and not force:
                self._log.info("DLE: '%s' ya está en la base de conocimiento (no se duplica)",
                               source.video_id)
                return {"status": "skipped", "documentary_id": source.video_id,
                        "doc_dir": self.store.doc_dir(source.video_id)}

            emit("analyzing")
            event(STARTED, "analyzing", doc_id=source.video_id)
            knowledge = self._analyze(source, work, errors, on_stage=emit, on_event=on_event)
            emit("storing")
            event(STARTED, "storing", doc_id=source.video_id,
                  scene_total=len(knowledge.scenes))
            paths = self.store.save(knowledge)
            return {"status": "learned", "documentary_id": source.video_id,
                    "knowledge": knowledge, "paths": paths, "doc_dir": self.store.doc_dir(source.video_id)}

    # ------------------------------------------------------------------ steps

    def _resolve_source(self, youtube, video, work, errors) -> VideoSource | None:
        try:
            if youtube:
                provider = self._youtube or _lazy_youtube()
                info = provider.resolve(youtube, work)
            elif video:
                provider = self._local or _lazy_local()
                info = provider.resolve(video, work)
            else:
                errors.append(AnalysisError("source", "no se indicó --youtube ni --video"))
                return None
            return VideoSource(**{k: info[k] for k in ("path", "source_type", "source_ref", "video_id")})
        except Exception as exc:  # noqa: BLE001
            errors.append(AnalysisError("source", str(exc)))
            return None

    def _analyze(self, source: VideoSource, work: str, errors: list,
                 on_stage=lambda _s: None, on_event=None) -> DocumentaryKnowledge:
        meta = Metadata(source_type=source.source_type, source_ref=source.source_ref,
                        video_id=source.video_id)
        try:
            probe = self.probe.probe(source.path)
            meta.duration = probe["duration"]
            meta.width, meta.height = probe["width"], probe["height"]
            meta.fps, meta.has_audio = probe["fps"], probe["has_audio"]
        except Exception as exc:  # noqa: BLE001
            errors.append(AnalysisError("metadata", str(exc)))

        cuts, silences, transcript = [], [], Transcript()
        try:
            cuts = self.probe.detect_cuts(source.path, threshold=self.scene_threshold)
        except Exception as exc:  # noqa: BLE001
            errors.append(AnalysisError("scene_detection", str(exc)))
        if meta.has_audio:
            try:
                silences = self.probe.silence_intervals(source.path)
            except Exception as exc:  # noqa: BLE001
                errors.append(AnalysisError("audio", str(exc)))
            try:
                transcript = self.transcriber.transcribe(source.path)
            except Exception as exc:  # noqa: BLE001
                errors.append(AnalysisError("transcription", str(exc)))

        shots = self._analyze_shots(source, meta, cuts, silences, transcript, work, errors,
                                    on_event=on_event)
        on_stage("learning")
        if on_event is not None:
            on_event(ProgressEvent(kind=STARTED, stage="learning", doc_id=source.video_id))
        scenes = group_into_scenes(shots)   # asigna scene_index a cada plano
        narrative = build_narrative_blocks(shots, meta.duration)
        stats = build_statistics(shots, scenes, meta.duration)

        return DocumentaryKnowledge(
            documentary_id=source.video_id, metadata=meta, scenes=scenes, shots=shots,
            narrative_blocks=narrative, statistics=stats, transcript=transcript, errors=errors,
        )

    def _analyze_shots(self, source, meta, cuts, silences, transcript, work, errors,
                       on_event=None):
        shots: list[ShotAnalysis] = []
        segments = cuts_to_shots(cuts, meta.duration)
        total = len(segments)
        frames_dir = os.path.join(work, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        for i, (start, end) in enumerate(segments):
            if on_event is not None:
                on_event(ProgressEvent(
                    kind=PROGRESS, stage="analyzing", doc_id=source.video_id,
                    shot_index=i + 1, shot_total=total,
                    percent=(i + 1) / total if total else 1.0,
                ))
            try:
                mid_t = start + (end - start) / 2.0
                mid = self.probe.extract_frame(source.path, mid_t,
                                               os.path.join(frames_dir, f"s{i:04d}_a.png"))
                mt = min(end - 0.05, mid_t + 0.4)
                motion = self.probe.extract_frame(source.path, mt,
                                                  os.path.join(frames_dir, f"s{i:04d}_b.png"))
                shots.append(analyze_shot(
                    index=i, scene_index=0, start=start, end=end,
                    mid_frame=mid, motion_frame=motion, silences=silences,
                    has_audio=meta.has_audio, transcript=transcript,
                ))
            except Exception as exc:  # noqa: BLE001 — un plano que falle no rompe el resto
                errors.append(AnalysisError(f"shot[{i}]", str(exc)))
                shots.append(ShotAnalysis(index=i, scene_index=0, start=round(start, 3),
                                          end=round(end, 3), duration=round(end - start, 3)))
        return shots


def _lazy_youtube():
    from app.dle.providers.youtube import YouTubeProvider
    return YouTubeProvider()


def _lazy_local():
    from app.dle.providers.local_video import LocalVideoProvider
    return LocalVideoProvider()
