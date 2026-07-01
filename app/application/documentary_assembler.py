"""DocumentaryAssembler — ensamblador de SECUENCIAS cinematográficas (refactor).

Cambio de paradigma: la unidad mínima de render YA NO es la escena, sino el
**Shot** generado por VIS. Flujo:

    Scene ─VIS-1─► VisualPlan ─VIS-2─► ExecutionPlan(ShotRequest[])
          ─MGL.generate_for_shot─► asset único por plano
          ─ShotProcessor.render──► clip por plano   ◄── hook Camera Motion
          ─FfmpegVideoComposer──► documental final (.mp4)

Cada escena contiene MÚLTIPLES planos y esa estructura se preserva hasta el
render. La narración de la escena se reparte (corte exacto, stdlib ``wave``) entre
sus planos, de modo que la voz es continua y la imagen cambia por plano
(sincronía narración↔imagen, ARCH-VIS-000 §8.1).

Camera Motion (Ken Burns/parallax/push-in) NO se implementa aún: el `ShotProcessor`
es el punto de extensión: un `CameraMotionShotProcessor` futuro implementará la
misma interfaz y aplicará ``shot.motion`` SIN tocar esta arquitectura.
"""

import contextlib
import os
import tempfile
import wave
from dataclasses import dataclass, field

from app.vai import VisualDirector, build_context
from app.vis import build_visual_plan

_MIN_SHOT_SECONDS = 1.0


@dataclass
class RenderShot:
    """Unidad mínima de render: un plano listo para convertirse en clip."""
    shot_id: str
    scene_id: str
    image_path: str
    audio_path: str | None
    duration: float
    motion: dict
    camera_move: str
    lens: str


@dataclass
class AssembledDocumentary:
    topic: str
    video_path: str
    rendered: bool
    scene_count: int
    shot_count: int
    report: dict = field(default_factory=dict)


class StillShotProcessor:
    """Procesador de plano por defecto: imagen fija (sin movimiento de cámara).

    HOOK de Camera Motion: un ``CameraMotionShotProcessor`` futuro implementará
    ``render(...)`` con la misma firma y usará ``shot.motion`` para aplicar
    Ken Burns/parallax/push-in, sin cambiar el assembler.
    """

    def __init__(self, normalizer) -> None:
        self._normalizer = normalizer

    def render(self, shot: RenderShot, out_clip: str) -> str:
        # ``motion`` se ignora por ahora (still). El futuro processor lo usará.
        return self._normalizer.scene_clip(
            shot.image_path, shot.audio_path, shot.duration, out_clip
        )


class DocumentaryAssembler:
    def __init__(
        self,
        mgl,
        synthesizer,
        normalizer=None,
        composer=None,
        shot_processor=None,
        director=None,
        *,
        output_dir: str = os.path.join("output", "documentary"),
        style: str = "documentary",
    ) -> None:
        self._mgl = mgl
        self._synthesizer = synthesizer
        self._normalizer = normalizer
        self._composer = composer
        # VAI: Director de Fotografía (Shot -> ShotExecutionRequest). Inyectable.
        self._director = director or VisualDirector()
        # Inyectable: por defecto still; sustituible por Camera Motion sin tocar nada.
        self._shot_processor = shot_processor or (
            StillShotProcessor(normalizer) if normalizer is not None else None
        )
        self._output_dir = output_dir
        self._style = style

    def assemble(self, scenes: list, *, profile, topic: str = "") -> AssembledDocumentary:
        """Ensambla la secuencia de planos de todas las escenas en un .mp4."""
        os.makedirs(self._output_dir, exist_ok=True)
        audio_dir = os.path.join(self._output_dir, "audio")
        os.makedirs(audio_dir, exist_ok=True)

        scenes_report: list[dict] = []
        render_shots: list[RenderShot] = []

        for scene in scenes or []:
            block = self._plan_scene(scene, profile, audio_dir)
            render_shots.extend(block["render_shots"])
            scenes_report.append(block["report"])

        video_path, rendered = self._render(render_shots)

        report = {
            "topic": topic,
            "style": self._style,
            "reference_profile": getattr(profile, "reference", ""),
            "scene_count": len(scenes_report),
            "shot_count": len(render_shots),
            "rendered": rendered,
            "video_path": video_path if rendered else "",
            "scenes": scenes_report,   # estructura escena -> planos preservada
        }
        return AssembledDocumentary(
            topic=topic,
            video_path=video_path if rendered else "",
            rendered=rendered,
            scene_count=len(scenes_report),
            shot_count=len(render_shots),
            report=report,
        )

    # --- planificación por escena (VIS-1 -> VIS-2 -> assets -> audio) --------

    def _plan_scene(self, scene, profile, audio_dir: str) -> dict:
        scene_id = str(getattr(scene, "id", "scene"))
        plan = build_visual_plan(profile, scene, style=self._style)          # VIS-1: estructura
        context = build_context(scene, profile, style=self._style)
        requests = [self._director.direct(ps, context) for ps in plan.shots]  # VAI: fotografía
        pairs = list(zip(plan.shots, requests))

        # 1) Un asset ÚNICO por plano (VAI produce prompts distintos por plano).
        images = [self._mgl.generate_for_shot(req).path for _, req in pairs]

        # 2) Narración de la escena (una voz por escena).
        narration = str(getattr(scene, "narration", ""))
        narr_path = os.path.join(audio_dir, f"{scene_id}.wav")
        narrated = False
        if narration.strip() and self._synthesizer is not None:
            try:
                narrated = bool(self._synthesizer.synthesize(narration, narr_path))
            except Exception:
                narrated = False

        vis_durations = [max(_MIN_SHOT_SECONDS, ps.duration) for ps, _ in pairs]

        # 3) Reparto del audio entre los planos (sincronía narración↔imagen).
        #    Partición EXACTA por fotogramas (proporcional a las duraciones de
        #    VIS): suma == duración del audio, sin trozos vacíos. La duración de
        #    cada clip la marca su trozo de audio (el normalizer usa -shortest).
        if narrated:
            slices = self._slice_wav(narr_path, vis_durations, audio_dir, scene_id)
            audio_slices = [path for path, _ in slices]
            durations = [dur if dur > 0 else vis_durations[i] for i, (_, dur) in enumerate(slices)]
        else:
            durations = vis_durations
            audio_slices = [None] * len(pairs)

        render_shots: list[RenderShot] = []
        shots_report: list[dict] = []
        for (ps, req), image, dur, audio in zip(pairs, images, durations, audio_slices):
            rs = RenderShot(
                shot_id=ps.id, scene_id=scene_id, image_path=image, audio_path=audio,
                duration=round(dur, 3), motion=req.motion, camera_move=ps.camera_move, lens=req.lens,
            )
            render_shots.append(rs)
            shots_report.append({
                "shot_id": ps.id, "shot_type": ps.shot_type, "lens": req.lens,
                "angle": req.angle, "composition": req.composition,
                "camera_move": ps.camera_move, "duration": rs.duration,
                "image": image, "narrated": audio is not None,
            })

        return {
            "render_shots": render_shots,
            "report": {"scene_id": scene_id, "shots": shots_report, "shot_count": len(shots_report)},
        }

    # --- render: plano -> clip -> composición --------------------------------

    def _render(self, render_shots: list[RenderShot]) -> tuple[str, bool]:
        out_path = os.path.join(self._output_dir, "documentary.mp4")
        if self._composer is None or self._shot_processor is None or not render_shots:
            return out_path, False
        if not all(s.image_path and os.path.exists(s.image_path) for s in render_shots):
            return out_path, False

        with tempfile.TemporaryDirectory() as clips_dir:
            clip_paths: list[str] = []
            for index, shot in enumerate(render_shots):
                clip = os.path.join(clips_dir, f"clip_{index:03d}.mkv")
                self._shot_processor.render(shot, clip)   # ◄ hook Camera Motion
                clip_paths.append(clip)
            self._composer.compose(clip_paths, out_path)

        ok = os.path.exists(out_path) and os.path.getsize(out_path) > 0
        return out_path, ok

    # --- utilidades de audio (stdlib wave; no toca el pipeline FFmpeg) -------

    @staticmethod
    def _wav_duration(path: str) -> float:
        try:
            with contextlib.closing(wave.open(path, "rb")) as handle:
                rate = handle.getframerate()
                if rate:
                    return handle.getnframes() / float(rate)
        except Exception:
            pass
        return _MIN_SHOT_SECONDS

    @staticmethod
    def _slice_wav(src: str, weights: list[float], out_dir: str, scene_id: str) -> list[tuple[str | None, float]]:
        """Parte el wav en trozos contiguos proporcionales a ``weights``.

        Garantías: Σ(fotogramas) == total (sin solapes ni huecos) y ningún trozo
        sobre-solicita fotogramas (evita wavs vacíos que romperían ffmpeg). Devuelve
        (ruta|None, duración_s); None si un trozo quedara a 0 fotogramas.
        """
        with contextlib.closing(wave.open(src, "rb")) as w:
            channels, sampwidth, framerate = w.getnchannels(), w.getsampwidth(), w.getframerate()
            total = w.getnframes()
            frames = w.readframes(total)
        bpf = sampwidth * channels
        wsum = sum(weights) or 1.0

        # Fotogramas por trozo, proporcionales y de suma EXACTA = total.
        counts: list[int] = []
        target = 0.0
        assigned = 0
        for i, weight in enumerate(weights):
            if i == len(weights) - 1:
                count = total - assigned
            else:
                target += (weight / wsum) * total
                count = int(round(target)) - assigned
            count = max(0, min(count, total - assigned))
            counts.append(count)
            assigned += count

        out: list[tuple[str | None, float]] = []
        cursor = 0
        for i, count in enumerate(counts):
            if count <= 0:
                out.append((None, 0.0))
                continue
            path = os.path.join(out_dir, f"{scene_id}_shot{i:02d}.wav")
            with contextlib.closing(wave.open(path, "wb")) as o:
                o.setnchannels(channels)
                o.setsampwidth(sampwidth)
                o.setframerate(framerate)
                o.writeframes(frames[cursor * bpf:(cursor + count) * bpf])
            out.append((path, count / float(framerate)))
            cursor += count
        return out
